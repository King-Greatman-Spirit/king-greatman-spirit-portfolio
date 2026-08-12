"""Pre-deploy sanity check for all integrations.

Run locally BEFORE pushing to the VPS:
    venv\\Scripts\\python.exe deploy_preflight.py

Safe to re-run any time. Only reads settings and does harmless API calls.
"""
import os
import sys
import re
import base64
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KingGreatmanSpirit.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django

django.setup()

import requests
from django.conf import settings
from django.core import mail
from django.test.utils import override_settings

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"
results = []


def check(name, ok, note, level=PASS):
    results.append((name, level if not ok else (PASS if level != WARN else WARN), note))


def get(key, default=""):
    return getattr(settings, key, default)


# ---------------------------------------------------------------------------
print("=" * 70)
print("KGS PRE-DEPLOY PREFLIGHT CHECK")
print("=" * 70)

# 1. SITE_URL ----------------------------------------------------------------
site_url = get("SITE_URL")
ok = bool(site_url) and site_url.startswith("https://") and not site_url.endswith("/")
check("SITE_URL", ok, f"{site_url}  (trailing-slash check: {'ok' if not site_url.endswith('/') else 'has /'})")

# 2. Google Search Console token ---------------------------------------------
gsc = get("GOOGLE_SITE_VERIFICATION")
ok = bool(gsc) and re.fullmatch(r"[A-Za-z0-9_-]{20,}", gsc or "")
check("GOOGLE_SITE_VERIFICATION", ok, f"{gsc[:8]}...{'len=' + str(len(gsc)) if gsc else '(missing)'}")

# 3. GA4 ---------------------------------------------------------------------
ga4 = get("GA4_MEASUREMENT_ID")
ok = bool(ga4) and ga4.startswith("G-") and len(ga4) == 13
check("GA4_MEASUREMENT_ID", ok, ga4 or "(missing)")

# 4. Flutterwave -------------------------------------------------------------
fw_pub = get("FLUTTERWAVE_PUBLIC_KEY", "")
fw_secret = get("FLUTTERWAVE_SECRET_KEY", "")
fw_wh = get("FLUTTERWAVE_WEBHOOK_SECRET", "")
ok = bool(fw_pub) and bool(fw_secret) and bool(fw_wh)
check("FLUTTERWAVE keys", ok, f"pub={bool(fw_pub)} secret={bool(fw_secret)} webhook_secret={bool(fw_wh)}")
mode = "TEST" if "FLWSECK_TEST" in fw_secret else "LIVE"
check("Flutterwave mode", fw_secret.startswith("FLWSECK_TEST") or fw_secret.startswith("FLWSECK"), f"secret prefix ok, mode={mode}")

# 5. Paystack ----------------------------------------------------------------
ps_pub = get("PAYSTACK_PUBLIC_KEY", "")
ps_secret = get("PAYSTACK_SECRET_KEY", "")
ok = bool(ps_pub) and bool(ps_secret)
check("PAYSTACK keys", ok, f"pub={bool(ps_pub)} secret={bool(ps_secret)}")
ps_mode = "TEST" if "pk_test" in ps_pub else "LIVE"
check("Paystack mode", ps_pub.startswith(("pk_live_", "pk_test_")), f"prefix ok, mode={ps_mode}")

# 6. Support notify ----------------------------------------------------------
wa = get("SUPPORT_NOTIFY_WHATSAPP_TO", "")
phone = get("SUPPORT_NOTIFY_PHONE", "")
email = get("SUPPORT_NOTIFY_EMAIL", "")
ok = bool(wa.startswith("whatsapp:+")) and bool(phone.startswith("+")) and bool(email)
check("SUPPORT_NOTIFY", ok, f"whatsapp={wa} phone={phone} email={email}")

# 7. Twilio ------------------------------------------------------------------
sid = get("TWILIO_ACCOUNT_SID", "")
token = get("TWILIO_AUTH_TOKEN", "")
wa_from = get("TWILIO_WHATSAPP_FROM", "")
if sid and token:
    ok, note = False, "keys present but must be verified by sending a message"
    try:
        r = requests.get(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json",
            auth=(sid, token), timeout=20,
        )
        ok = r.status_code == 200
        note = f"Twilio API auth: HTTP {r.status_code}"
    except Exception as exc:
        note = f"Twilio API unreachable: {exc}"
    check("TWILIO", ok, note)
    check("TWILIO_WHATSAPP_FROM", bool(wa_from), wa_from)
else:
    check("TWILIO", True, "not configured -> EMAIL fallback is active (no SID/TOKEN)", WARN)

# 8. Email SMTP (Gmail app password) -----------------------------------------
try:
    with override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"):
        with mail.get_connection() as conn:
            conn.open()
    check("EMAIL SMTP", True, f"{get('EMAIL_HOST')}:{get('EMAIL_PORT')} TLS={get('EMAIL_USE_TLS')}")
except Exception as exc:
    check("EMAIL SMTP", False, str(exc))

# 9. Binance key/signature ---------------------------------------------------
binance_api = get("BINANCE_API_KEY", "")
binance_pk = get("BINANCE_PRIVATE_KEY", "")
if binance_api and binance_pk:
    from cryptography.hazmat.primitives import serialization
    try:
        pem = binance_pk.replace("\\n", "\n")
        key = serialization.load_pem_private_key(pem.encode(), password=None)
        key.sign(b"preflight-test")
        check("BINANCE key+sign", True, f"{type(key).__name__} loads and signs OK")
    except Exception as exc:
        check("BINANCE key+sign", False, f"{type(exc).__name__}: {exc}")
    try:
        r = requests.post(
            "https://bpay.binanceapi.com/binancepay/openapi/v2/order",
            json={}, timeout=15,
        )
        check("BINANCE reachability", False if r.status_code in (403, 404) else True,
              f"HTTP {r.status_code} from this network"
              + (" -> geo-blocked (expected from Nigeria), test from VPS instead" if r.status_code == 403 else ""))
    except Exception as exc:
        check("BINANCE reachability", False, f"unreachable: {exc} (test from VPS)")
else:
    check("BINANCE", True, "not configured", WARN)

# 10. Live API auth spot-checks ----------------------------------------------
print("\n-- live gateway auth spot-checks --")
try:
    r = requests.get(
        "https://api.flutterwave.com/v3/banks/NG",
        headers={"Authorization": f"Bearer {fw_secret}"}, timeout=20,
    )
    check("Flutterwave API auth", r.status_code == 200, f"GET /v3/banks/NG -> HTTP {r.status_code}")
except Exception as exc:
    check("Flutterwave API auth", False, f"unreachable: {exc}")

try:
    r = requests.get(
        "https://api.paystack.co/balance",
        headers={"Authorization": f"Bearer {ps_secret}"}, timeout=20,
    )
    check("Paystack API auth", r.status_code == 200, f"GET /balance -> HTTP {r.status_code}")
    if r.status_code == 200:
        for b in r.json().get("data", []):
            print(f"        balance: {b.get('currency')} {b.get('balance', 0) / 100:.2f}")
except Exception as exc:
    check("Paystack API auth", False, f"unreachable: {exc}")

# 11. Security flags ----------------------------------------------------------
check("DEBUG", settings.DEBUG is False,
      f"DEBUG={settings.DEBUG} -> set DEBUG=False in .env on the VPS", WARN if settings.DEBUG else PASS)
hosts = ",".join(get("ALLOWED_HOSTS", []))
check("ALLOWED_HOSTS", "kinggreatmanspirit.com" in hosts, hosts)

# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
failed = False
for name, level, note in results:
    icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}[level]
    print(f"{icon} {name:<32} {note}")
    if level == "FAIL":
        failed = True
print("=" * 70)
if failed:
    print("RESULT: FIX THE [FAIL] ITEMS BEFORE DEPLOYING")
    sys.exit(1)
else:
    print("RESULT: READY TO DEPLOY (WARN items are optional/expected)")
    sys.exit(0)
