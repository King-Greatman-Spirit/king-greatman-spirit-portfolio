import base64
import json
import time
import uuid

import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

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
        "binance_ready": bool(settings.BINANCE_API_KEY and settings.BINANCE_PRIVATE_KEY),
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


def binance_create_order(request, reference):
    """Create a Binance Pay order server-side and return the QR content as JSON."""
    payment = get_object_or_404(PaymentRequest, reference=reference)

    if not (settings.BINANCE_API_KEY and settings.BINANCE_PRIVATE_KEY):
        return _json({"ok": False, "error": "Binance Pay is not configured yet."})

    body = {
        "env": {"terminalType": "APP"},
        "merchantTradeNo": payment.reference,
        "orderAmount": str(payment.amount),
        "currency": payment.currency if payment.currency == "USDT" else "USDT",
        "goods": {
            "goodsType": "01",
            "goodsCategory": "D000",
            "referenceGoodsId": "KGS-" + str(payment.pk),
            "goodsName": payment.service.name if payment.service else "King Greatman Spirit Services",
            "goodsDetail": payment.description or "Payment for services",
        },
    }

    try:
        order_resp = _binance_request(BINANCE_ORDER_URL, body)
        if order_resp.get("status") != "SUCCESS" or not order_resp.get("data", {}).get("prepayId"):
            return _json({"ok": False, "error": order_resp.get("errorMessage", "Binance order creation failed.")})

        prepay_id = order_resp["data"]["prepayId"]
        qr_resp = _binance_request(BINANCE_QR_URL, {"prepayId": prepay_id})
        if qr_resp.get("status") != "SUCCESS" or not qr_resp.get("data", {}).get("qrContent"):
            return _json({"ok": False, "error": qr_resp.get("errorMessage", "QR generation failed.")})

        return _json({"ok": True, "qr": qr_resp["data"]["qrContent"]})
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
    resp.raise_for_status()
    return resp.json()


def _binance_sign(payload):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    private_key_pem = settings.BINANCE_PRIVATE_KEY.replace("\\n", "\n")
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
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


def payment_success(request, reference):
    payment = get_object_or_404(PaymentRequest, reference=reference)
    return render(request, "payments/success.html", {"payment": payment})


def payment_pending(request, reference):
    payment = get_object_or_404(PaymentRequest, reference=reference)
    return render(request, "payments/pending.html", {"payment": payment})


def payment_failed(request, reference):
    payment = get_object_or_404(PaymentRequest, reference=reference)
    return render(request, "payments/failed.html", {"payment": payment})


def _json(payload):
    from django.http import JsonResponse
    return JsonResponse(payload)
