from django.shortcuts import render, redirect
from django.contrib import messages

from .models import ContactMessage, Socials, NewsletterSubscriber, CHANNEL_CHOICES
from .validation import (
    autocorrect_email,
    autocorrect_message,
    autocorrect_name,
    autocorrect_phone,
    validate_contact_payload,
    validate_subscribe_email,
)
from .emails import (
    BASE_URL,
    send_contact_notification,
    send_contact_confirmation,
    send_newsletter_confirmation,
)
from service.models import Service


def contact(request):
    title = "Contact Us"
    socials = Socials.objects.first()
    services = Service.objects.all()

    if request.method == "POST":
        data = request.POST

        # Honeypot — bots fill hidden fields, humans don't. Silently drop.
        if data.get("website"):
            return redirect("contact")

        full_name = autocorrect_name(data.get("full_name"))
        email = autocorrect_email(data.get("email"))
        phone = autocorrect_phone(data.get("phone_number"))
        message = autocorrect_message(data.get("message"))

        errors = validate_contact_payload(full_name, email, phone, message)
        if errors:
            for err in errors:
                messages.error(request, err)
            context = {
                "title": title,
                "socials": socials,
                "services": services,
                "channel_choices": CHANNEL_CHOICES,
                "form_data": {
                    "full_name": full_name,
                    "email": email,
                    "phone_number": phone,
                    "company_name": (data.get("company_name") or "").strip(),
                    "service": data.get("service") or "",
                    "channel": data.get("channel") or "",
                    "message": message,
                },
            }
            return render(request, "home.html", context)

        contact = ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone or None,
            company_name=(data.get("company_name") or "").strip(),
            service_id=data.get("service") or None,
            channel=data.get("channel") or "",
            referral=data.get("referral") or "Direct",
            message=message,
        )

        send_contact_notification(contact)
        send_contact_confirmation(contact)

        messages.success(
            request,
            "Thank you for reaching out to King Greatman Spirit. Your message has been "
            "received successfully and is currently under review. We will respond shortly "
            "with a tailored and value-driven response."
        )

        return redirect("contact")

    context = {
        "title": title,
        "socials": socials,
        "services": services,
        "channel_choices": CHANNEL_CHOICES,
    }
    return render(request, "home.html", context)


def subscribe(request):
    """Newsletter signup — validates strictly, saves and sends a confirmation email."""
    if request.method == "POST":
        data = request.POST

        # Honeypot — pretend success to bot scripts.
        if data.get("website"):
            messages.success(
                request,
                "You're subscribed! 🎉 Check your inbox for a welcome email — see you in the Inner Circle."
            )
            return redirect(data.get("next") or "home")

        email = autocorrect_email(data.get("email"))
        source = (data.get("source") or "Website").strip()[:100]

        error = validate_subscribe_email(email)
        if error:
            messages.error(request, error)
            next_url = data.get("next") or request.META.get("HTTP_REFERER") or "home"
            if not next_url.startswith("/"):
                next_url = "home"
            return redirect(next_url)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={"is_active": True, "source": source},
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()

        unsubscribe_url = BASE_URL + "/newsletter/unsubscribe/" + subscriber.email + "/"
        send_newsletter_confirmation(subscriber, unsubscribe_url)

        messages.success(
            request,
            "You're subscribed! 🎉 Check your inbox for a welcome email — see you in the Inner Circle."
        )

        next_url = data.get("next") or request.META.get("HTTP_REFERER") or "home"
        if not next_url.startswith("/"):
            next_url = "home"
        return redirect(next_url)

    return redirect("home")


def unsubscribe(request, email):
    """Deactivate a newsletter subscription (linked from the confirmation email)."""
    subscriber = NewsletterSubscriber.objects.filter(email=email.lower()).first()
    if subscriber:
        subscriber.is_active = False
        subscriber.save()
    return render(request, "newsletter/unsubscribed.html", {"email": email})


def email_preview(request, name):
    """DEBUG-only browser preview of the HTML emails (images load locally)."""
    from django.conf import settings
    from django.http import Http404, HttpResponse
    from django.utils import timezone
    from django.template.loader import render_to_string

    if not settings.DEBUG:
        raise Http404

    from .emails import preview_context
    from payments.models import PaymentRequest
    from service.models import Service

    base = request.build_absolute_uri("/").rstrip("/")
    ctx = preview_context(base_url=base)
    templates = {
        "newsletter": ("emails/newsletter_confirmation_email.html", {
            "subscriber": NewsletterSubscriber(email="your@email.com"),
            "unsubscribe_url": base + "/newsletter/unsubscribe/your@email.com/",
        }),
        "contact-confirmation": ("emails/contact_confirmation_email.html", {
            "contact": ContactMessage(full_name="John Doe", email="john@example.com", message="Hi King! I need a modern website for my clothing brand and maybe a mobile app later."),
        }),
        "contact-notification": ("emails/contact_notification_email.html", {
            "contact": ContactMessage(
                full_name="John Doe", email="john@example.com", phone_number="+234 901 415 5705",
                company_name="John's Fashion", channel="WhatsApp", referral="Direct",
                service=Service.objects.first(),
                message="Hi King! I need a modern website for my clothing brand and maybe a mobile app later.",
            ),
            "received_time": timezone.now(),
        }),
        "payment-receipt": ("emails/payment_receipt_email.html", {
            "payment": PaymentRequest(
                full_name="John Doe", email="john@example.com", reference="KGS-PREVIEW0000001",
                amount=500000, currency="NGN", method="flutterwave",
                service=Service.objects.first(), description="Business website deposit",
                status="paid", paid_date=timezone.now(),
            ),
        }),
    }
    if name not in templates:
        raise Http404

    template, extra = templates[name]
    ctx.update(extra)
    html = render_to_string(template, ctx)
    return HttpResponse(html, content_type="text/html; charset=utf-8")
