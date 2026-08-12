import base64
import json
import time
import uuid

import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from contact.emails import send_payment_receipt
from service.models import Service

from .models import PAYMENT_METHODS, CURRENCIES, PaymentRequest

FLUTTERWAVE_VERIFY_URL = "https://api.flutterwave.com/v3/transactions/verify_by_reference"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify"
BINANCE_ORDER_URL = "https://bpay.binanceapi.com/binancepay/openapi/v2/order"
BINANCE_QR_URL = "https://bpay.binanceapi.com/binancepay/openapi/v2/qr"


def payment_page(request):
    """Step 1: choose service / amount / method."""
    title = "Pay Now"
    services = Service.objects.all()

    if request.method == "POST":
        data = request.POST
        full_name = (data.get("full_name") or "").strip()
        email = (data.get("email") or "").strip()
        amount = (data.get("amount") or "").strip()
        method = data.get("method")
        currency = data.get("currency") or "NGN"

        if not full_name or not email:
            messages.error(request, "Please provide your full name and email address.")
            return redirect("payments:payment_page")
        try:
            amount = round(float(amount), 2)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid amount greater than zero.")
            return redirect("payments:payment_page")
        if method not in dict(PAYMENT_METHODS):
            messages.error(request, "Please choose a payment method.")
            return redirect("payments:payment_page")

        payment = PaymentRequest.objects.create(
            full_name=full_name,
            email=email,
            phone_number=(data.get("phone_number") or "").strip() or None,
            service_id=data.get("service") or None,
            description=(data.get("description") or "").strip() or None,
            amount=amount,
            currency=currency,
            method=method,
        )
        return redirect("payments:payment_gateway", reference=payment.reference)

    context = {
        "title": title,
        "services": services,
        "methods": PAYMENT_METHODS,
        "currencies": CURRENCIES,
        "flutterwave_ready": bool(settings.FLUTTERWAVE_PUBLIC_KEY),
        "paystack_ready": bool(settings.PAYSTACK_PUBLIC_KEY),
        # Binance re-enable checklist (see binance_create_order below):
        #   1. BINANCE_ENABLED=True          (this switch, in .env)
        #   2. BINANCE_MERCHANT_ID           (from the Merchant Management Portal)
        #   3. Build the payment-confirmation flow (webhook + order query)
        #      -- without it, paid orders are never confirmed & receipts never send.
        "binance_enabled": bool(
            settings.BINANCE_API_KEY
            and settings.BINANCE_PRIVATE_KEY
            and settings.BINANCE_MERCHANT_ID
            and settings.BINANCE_ENABLED
        ),
    }
    return render(request, "payments/payment.html", context)


def payment_gateway(request, reference):
    """Step 2: run the gateway checkout (Flutterwave inline / Paystack popup / Binance QR)."""
    payment = get_object_or_404(PaymentRequest, reference=reference)

    if payment.status == "paid":
        return redirect("payments:payment_success", reference=payment.reference)

    if payment.method == "flutterwave":
        if not settings.FLUTTERWAVE_PUBLIC_KEY:
            return render(request, "payments/gateway_manual.html", {"payment": payment})
        return render(request, "payments/gateway_flutterwave.html", {
            "payment": payment,
            "public_key": settings.FLUTTERWAVE_PUBLIC_KEY,
        })

    if payment.method == "paystack":
        if not settings.PAYSTACK_PUBLIC_KEY:
            return render(request, "payments/gateway_manual.html", {"payment": payment})
        return render(request, "payments/gateway_paystack.html", {
            "payment": payment,
            "public_key": settings.PAYSTACK_PUBLIC_KEY,
        })

    if payment.method == "binance":
        return render(request, "payments/gateway_binance.html", {"payment": payment})

    messages.error(request, "Unsupported payment method.")
    return redirect("payments:payment_page")


NONCE_RATE_CACHE = {}


def _ngn_to_usdt(ngn_amount, budget=60):
    """Convert naira to USDT for the Binance order.

    Uses a live USD/NGN rate (with a small buffer, rounded UP so the merchant
    never receives less than the naira amount). Falls back to the manual
    BINANCE_NGN_USDT_RATE from .env if the live rate can't be fetched.
    Returns a USDT string, or None if no rate is available.
    """
    import math

    rate = NONCE_RATE_CACHE.get("rate")
    if not rate:
        manual = getattr(settings, "BINANCE_NGN_USDT_RATE", "")
        try:
            r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=budget)
            r.raise_for_status()
            rate = float(r.json()["rates"]["NGN"])
            NONCE_RATE_CACHE["rate"] = rate
        except Exception:
            try:
                rate = float(manual)
            except (TypeError, ValueError):
                return None
    # +1% buffer, round up to 4 decimals so we never undercharge.
    usdt = math.ceil(ngn_amount / rate * 1.01 * 10000) / 10000
    return f"{usdt:.4f}"


# ---------------------------------------------------------------
# BINANCE PAY (status: CODE READY, MERCHANT PENDING, OPTION HIDDEN)
#
# Everything below is functional and was fixed/verified:
#   - v2 order payload (merchantId + tradeType + totalFee...)  [was v1 format -> 401]
#   - Ed25519 private-key signing (auto-detected vs RSA)
#   - NGN -> USDT conversion with +1% buffer, rounded UP (no more
#     "NGN 200 becomes $200" overcharging)
#   - Clean error messages from Binance (no raw URLs)
#   - Friendly "You'll pay X USDT (approx NGN)" on the QR page
#
# Still required before re-enabling (see .env BINANCE_ENABLED):
#   1. Merchant account fully approved (entity verification + agreement)
#   2. BINANCE_MERCHANT_ID from the Merchant Management Portal
#   3. Payment confirmation flow: webhook endpoint + order-query poll
#      so paid orders get status=paid and the receipt email fires
# ---------------------------------------------------------------
def binance_create_order(request, reference):
    """Create a Binance Pay order server-side and return the QR content as JSON."""
    payment = get_object_or_404(PaymentRequest, reference=reference)

    if not (settings.BINANCE_API_KEY and settings.BINANCE_PRIVATE_KEY):
        return _json({"ok": False, "error": "Binance Pay is not configured yet."})
    if not settings.BINANCE_MERCHANT_ID:
        return _json({"ok": False, "error": "Binance's Merchant ID is missing — the owner needs to add it."})

    total_fee = str(payment.amount)
    if payment.currency != "USDT":
        total_fee = _ngn_to_usdt(payment.amount)
        if not total_fee:
            return _json({"ok": False, "error": "Couldn't fetch the NGN/USDT rate right now — please try again in a moment."})

    body = {
        "merchantId": settings.BINANCE_MERCHANT_ID,
        "merchantTradeNo": payment.reference,
        "tradeType": "WEB",
        "totalFee": total_fee,
        "currency": "USDT",
        "productName": payment.service.name if payment.service else "King Greatman Spirit Services",
        "productType": "Goods",
        "productDetail": payment.description or "Payment for services",
        "timeout": 60,
    }

    try:
        order_resp = _binance_request(BINANCE_ORDER_URL, body)
        if order_resp.get("status") != "SUCCESS" or not order_resp.get("data", {}).get("prepayId"):
            return _json({"ok": False, "error": order_resp.get("errorMessage", "Binance order creation failed.")})

        prepay_id = order_resp["data"]["prepayId"]
        qr_resp = _binance_request(BINANCE_QR_URL, {"prepayId": prepay_id})
        if qr_resp.get("status") != "SUCCESS" or not qr_resp.get("data", {}).get("qrContent"):
            return _json({"ok": False, "error": qr_resp.get("errorMessage", "QR generation failed.")})

        return _json({
            "ok": True,
            "qr": qr_resp["data"]["qrContent"],
            "usdt": body["totalFee"],
            "currency": "USDT",
            "original_amount": str(payment.amount),
            "original_currency": payment.currency,
        })
    except Exception as exc:  # noqa: BLE001
        return _json({"ok": False, "error": str(exc)})


def _binance_request(url, body):
    timestamp = str(int(time.time() * 1000))
    nonce = uuid.uuid4().hex
    payload = f"{timestamp}\n{nonce}\n{json.dumps(body)}\n"
    signature = _binance_sign(payload)
    headers = {
        "Content-Type": "application/json",
        "BinancePay-Timestamp": timestamp,
        "BinancePay-Nonce": nonce,
        "BinancePay-Certificate-SN": settings.BINANCE_API_KEY,
        "BinancePay-Signature": signature,
    }
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    if resp.status_code >= 400:
        try:
            err = resp.json()
            msg = (
                err.get("errorMessage")
                or err.get("message")
                or err.get("errorMsg")
                or f"Binance error (HTTP {resp.status_code})"
            )
        except ValueError:
            msg = f"Binance error (HTTP {resp.status_code}) — please try again"
        raise RuntimeError(msg)
    return resp.json()


def _binance_sign(payload):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    private_key_pem = settings.BINANCE_PRIVATE_KEY.replace("\\n", "\n")
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    try:
        # Ed25519 keys sign the payload directly (no padding/hash)
        signature = private_key.sign(payload.encode())
    except TypeError:
        # RSA keys use PKCS#1 v1.5 + SHA-256
        signature = private_key.sign(payload.encode(), padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(signature).decode()


def verify_flutterwave(request, reference):
    payment = get_object_or_404(PaymentRequest, reference=reference)
    if not settings.FLUTTERWAVE_SECRET_KEY:
        return redirect("payments:payment_pending", reference=payment.reference)

    try:
        resp = requests.get(
            FLUTTERWAVE_VERIFY_URL,
            params={"tx_ref": payment.reference},
            headers={"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"},
            timeout=30,
        )
        data = resp.json().get("data", {})
        if resp.json().get("status") == "success" and data.get("status") == "successful":
            _mark_paid(payment, data.get("id"))
            return redirect("payments:payment_success", reference=payment.reference)
        payment.gateway_response = json.dumps(data)[:4000]
        payment.save()
        return redirect("payments:payment_failed", reference=payment.reference)
    except Exception as exc:  # noqa: BLE001
        payment.gateway_response = str(exc)[:4000]
        payment.save()
        return redirect("payments:payment_failed", reference=payment.reference)


def verify_paystack(request, reference):
    payment = get_object_or_404(PaymentRequest, reference=reference)
    if not settings.PAYSTACK_SECRET_KEY:
        return redirect("payments:payment_pending", reference=payment.reference)

    try:
        resp = requests.get(
            f"{PAYSTACK_VERIFY_URL}/{payment.reference}",
            headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
            timeout=30,
        )
        data = resp.json().get("data", {})
        if resp.json().get("status") and data.get("status") == "success":
            _mark_paid(payment, data.get("reference"))
            return redirect("payments:payment_success", reference=payment.reference)
        payment.gateway_response = json.dumps(data)[:4000]
        payment.save()
        return redirect("payments:payment_failed", reference=payment.reference)
    except Exception as exc:  # noqa: BLE001
        payment.gateway_response = str(exc)[:4000]
        payment.save()
        return redirect("payments:payment_failed", reference=payment.reference)


def _mark_paid(payment, gateway_ref):
    payment.status = "paid"
    payment.gateway_ref = str(gateway_ref)[:200]
    payment.paid_date = timezone.now()
    payment.save()
    send_payment_receipt(payment)


# ---------------------------------------------------------------
# flutterwave_webhook()
# Entry point for Flutterwave server-to-server notifications
# (the URL you enter under Developers -> Webhooks on their
# dashboard). CSRF is disabled because Flutterwave cannot send
# a CSRF token; instead we trust the "verif-hash" header, which
# must match FLUTTERWAVE_WEBHOOK_SECRET in the .env file.
# This marks payments paid even if the customer closed the
# browser before the redirect back to our site completed.
# ---------------------------------------------------------------
@csrf_exempt
def flutterwave_webhook(request):
    # Flutterwave only ever POSTs JSON here; anything else is noise.
    if request.method != "POST":
        return _json({"status": "error", "message": "POST only"})

    # Security: reject anything without the matching secret hash.
    if request.headers.get("verif-hash") != settings.FLUTTERWAVE_WEBHOOK_SECRET:
        return _json({"status": "error", "message": "Invalid verif-hash"}, status=401)

    try:
        payload = json.loads(request.body)
    except (ValueError, TypeError):
        return _json({"status": "error", "message": "Invalid JSON body"})

    event = payload.get("event", "")
    data = payload.get("data") or {}

    # Only the "charge completed" events represent a successful payment;
    # v3 sends "charge.completed" (with status inside data), the legacy
    # format sends "charge.success". Everything else (refunds, payouts,
    # transfers) is ignored so we never mark a payment paid by mistake.
    if event in ("charge.completed", "charge.success"):
        if data.get("status") and data["status"] != "successful":
            return _json({"status": "ok", "message": "Ignored - not successful"})

        # tx_ref is our own payment reference (used in gateway_flutterwave.html).
        reference = data.get("tx_ref")
        if not reference:
            return _json({"status": "error", "message": "Missing tx_ref"})

        payment = PaymentRequest.objects.filter(reference=reference).first()
        if not payment:
            return _json({"status": "error", "message": "Unknown reference"}, status=404)

        # Idempotent: if already paid, still answer 200 so Flutterwave
        # stops retrying this event.
        if payment.status != "paid":
            _mark_paid(payment, data.get("id"))
        return _json({"status": "success", "message": "Payment confirmed"})

    # Acknowledged event types we don't act on - always 200 so
    # Flutterwave stops retrying them.
    return _json({"status": "ok", "message": f"Ignored event: {event}"})


def payment_success(request, reference):
    payment = get_object_or_404(PaymentRequest, reference=reference)
    return render(request, "payments/success.html", {"payment": payment})


def payment_pending(request, reference):
    payment = get_object_or_404(PaymentRequest, reference=reference)
    return render(request, "payments/pending.html", {"payment": payment})


def payment_failed(request, reference):
    payment = get_object_or_404(PaymentRequest, reference=reference)
    return render(request, "payments/failed.html", {"payment": payment})


def _json(payload, status=200):
    from django.http import JsonResponse
    return JsonResponse(payload, status=status)
