"""Instant alerts when someone asks for live support.

Priority:
  1. WhatsApp message  (Twilio WhatsApp API)
  2. SMS message        (Twilio SMS API)
  3. Email fallback     (Gmail SMTP — always attempted if 1 & 2 unavailable)

Add your (free) Twilio credentials in .env to activate WhatsApp + SMS.
"""
import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _twilio_send(recipient, body, sender):
    sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    if not sid or not token or not recipient or not sender:
        return False
    try:
        resp = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            data={"To": recipient, "From": sender, "Body": body},
            auth=(sid, token),
            timeout=20,
        )
        return resp.status_code == 201
    except Exception as exc:  # noqa: BLE001
        logger.warning("Twilio send failed: %s", exc)
        return False


def _phone_digits(phone):
    return "".join(ch for ch in (phone or "") if ch.isdigit())


def notify_ticket(ticket):
    """Alert the owner about a new support ticket. Returns a dict of results."""
    results = {"whatsapp": False, "sms": False, "email": False}

    contact = f"{ticket.full_name}"
    if ticket.phone_number:
        contact += f"  (tel: {ticket.phone_number})"
    if ticket.email:
        contact += f"  (mail: {ticket.email})"

    wa_body = (
        f"\U0001F3AB NEW SUPPORT TICKET — someone wants to talk to you LIVE\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Name: {ticket.full_name}\n"
        f"Phone: {ticket.phone_number or 'not given'}\n"
        f"Email: {ticket.email or 'not given'}\n"
        f"Topic: {ticket.topic or 'General'}\n\n"
        f"Message: {ticket.message[:300]}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Tap here to chat them instantly on WhatsApp:\n"
        f"https://wa.me/{_phone_digits(ticket.phone_number or ticket.email)}"
    )

    sms_body = (
        f"[KGS] Live-support request from {ticket.full_name}"
        f" ({ticket.phone_number or ticket.email}):"
        f" {ticket.message[:110]}"
    )

    results["whatsapp"] = _twilio_send(
        settings.SUPPORT_NOTIFY_WHATSAPP_TO, wa_body, settings.TWILIO_WHATSAPP_FROM
    )
    results["sms"] = _twilio_send(
        settings.SUPPORT_NOTIFY_PHONE, sms_body, settings.TWILIO_SMS_FROM
    )

    if not (results["whatsapp"] or results["sms"]):
        subject = f"\U0001F3AB New support ticket from {ticket.full_name}"
        html = render_to_string(
            "dashboard/emails/ticket_alert.html",
            {"ticket": ticket, "ticket_admin_url": settings.SITE_URL + "/dashboard/tickets/"},
        )
        try:
            send_mail(
                subject,
                strip_tags(html),
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPPORT_NOTIFY_EMAIL],
                html_message=html,
                fail_silently=False,
            )
            results["email"] = True
        except Exception as exc:  # noqa: BLE001
            logger.error("Support ticket email alert failed: %s", exc)

    return results
