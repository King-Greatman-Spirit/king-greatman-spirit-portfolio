import hashlib
import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from about.models import About
from contact.models import Socials

BASE_URL = getattr(settings, "SITE_URL", "https://kinggreatmanspirit.com")

# Favicon-based brand icons (official platform icons, sized for email)
_SOCIAL_ICONS = [
    ("facebook", "facebook.com", "Facebook", "#1877f2"),
    ("twitter", "x.com", "X", "#000000"),
    ("instagram", "instagram.com", "Instagram", "#e1306c"),
    ("linkedin", "linkedin.com", "LinkedIn", "#0a66c2"),
    ("github", "github.com", "GitHub", "#181717"),
    ("youTube", "youtube.com", "YouTube", "#ff0000"),
    ("tiktok", "tiktok.com", "TikTok", "#010101"),
    ("telegram", "t.me", "Telegram", "#26a5e4"),
    ("threads", "threads.com", "Threads", "#111111"),
    ("medium", "medium.com", "Medium", "#000000"),
    ("substack", "substack.com", "Substack", "#ff6719"),
    ("pinterest", "pinterest.com", "Pinterest", "#e60023"),
    ("whatsapp", "wa.me", "WhatsApp", "#25d366"),
]

FAVICON_URL = "https://www.google.com/s2/favicons?domain={domain}&sz=64"


def social_items():
    """Only the social links that are actually filled in, with their favicon URL."""
    socials = Socials.objects.first()
    items = []
    if not socials:
        return items
    for field, domain, label, color in _SOCIAL_ICONS:
        url = getattr(socials, field, None)
        if url:
            items.append(
                {
                    "name": label,
                    "url": url,
                    "icon": FAVICON_URL.format(domain=domain),
                    "color": color,
                }
            )
    return items


def _absolute_image(path):
    if not path:
        return None
    return BASE_URL + path


def _base_context():
    about = About.objects.first()
    ctx = {
        "base_url": BASE_URL,
        "about_links": about,
        "socials_links": Socials.objects.first(),
        "social_items": social_items(),
        "avatar_src": None,
        "cover_src": None,
        "profile_src": None,
        "portrait_src": None,   # "The Man Behind the Work" portrait
    }
    if about:
        ctx.update(
            {
                "avatar_src": "cid:kgs_avatar",
                "cover_src": "cid:kgs_cover",
                "profile_src": "cid:kgs_profile",
            }
        )
    return ctx


def _mimetype(path):
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(os.path.splitext(path)[1].lower(), "image/jpeg")


def _attach_inline(email, field, cid):
    """Attach an image as an inline (CID) attachment so it ALWAYS renders in
    the email — even when the reader blocks external images."""
    if not field:
        return None
    try:
        from email.mime.image import MIMEImage

        with field.open("rb") as f:
            part = MIMEImage(f.read(), _subtype=_mimetype(f.name).split("/")[1])
        part.add_header("Content-ID", f"<{cid}>")
        part.add_header("Content-Disposition", "inline", filename=os.path.basename(field.name))
        email.attach(part)
        return f"cid:{cid}"
    except (OSError, ValueError):
        return _absolute_image(field.url)


def _attach_file(email, path, cid, url):
    """Attach a plain file (not a model field) as an inline image.

    Used for the "King Greatman Spirit" portrait that the main website
    shows in "The Man Behind the Work" — it lives in media/ directly,
    not on a model, so it needs its own attachment path."""
    if not path or not os.path.exists(path):
        return None
    try:
        from email.mime.image import MIMEImage

        with open(path, "rb") as f:
            part = MIMEImage(f.read(), _subtype=_mimetype(path).split("/")[1])
        part.add_header("Content-ID", f"<{cid}>")
        part.add_header("Content-Disposition", "inline", filename=os.path.basename(path))
        email.attach(part)
        return f"cid:{cid}"
    except (OSError, ValueError):
        return url


def _portrait_file():
    """Locate the portrait used on the site: king-greatman-spirit.png,
    falling back to spiritual.png."""
    for name in ("king-greatman-spirit.png", "spiritual.png"):
        candidate = os.path.join(settings.MEDIA_ROOT, "about_images", name)
        if os.path.exists(candidate):
            return candidate, f"{settings.MEDIA_URL}about_images/{name}"
    return "", ""


def send_html_email(subject, template_name, context, to_list, reply_to=None, base_url=None):
    """Render a Django template as HTML email with inline images and send it."""
    global BASE_URL
    if base_url:
        BASE_URL = base_url

    about = About.objects.first()
    ctx = _base_context()
    ctx.update(context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_list,
        reply_to=reply_to or [],
    )

    if about:
        # Only the avatar and cover images are attached here — they are the
        # header images every email displays. The about_image (kgs_profile)
        # is NOT attached: no template uses it anymore, and an unused inline
        # attachment shows up as a stray file (e.g. "yeah.jpg") in Gmail's
        # attachment row next to "Scanned by Gmail".
        for cid, field_name in (
            ("kgs_avatar", "profile_image"),
            ("kgs_cover", "cover_image"),
        ):
            field = getattr(about, field_name, None)
            src = _attach_inline(email, field, cid)
            if src:
                key = {"kgs_avatar": "avatar_src", "kgs_cover": "cover_src"}[cid]
                ctx[key] = src

    # Attach the "The Man Behind the Work" portrait (the same image the
    # main website shows) so newsletter emails can use it as their image.
    portrait_path, portrait_url = _portrait_file()
    # Unique Content-ID per file: Gmail caches inline images by Content-ID,
    # so a static ID (e.g. kgs_portrait) would keep showing the OLD image
    # even after the file changes. Hashing the path makes the ID change
    # whenever the picture changes, forcing Gmail to re-fetch it.
    portrait_cid = "kgs_portrait_" + hashlib.md5(portrait_path.encode()).hexdigest()[:10]
    portrait_src = _attach_file(email, portrait_path, portrait_cid, BASE_URL + portrait_url)
    if portrait_src:
        ctx["portrait_src"] = portrait_src

    html_body = render_to_string(template_name, ctx)
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=True)
    return True


def preview_context(base_url=None):
    """Context for browser previews — image srcs as absolute URLs (not cid)."""
    global BASE_URL
    if base_url:
        BASE_URL = base_url
    ctx = _base_context()
    about = ctx["about_links"]
    if about:
        if about.profile_image:
            ctx["avatar_src"] = BASE_URL + about.profile_image.url
        if about.cover_image:
            ctx["cover_src"] = BASE_URL + about.cover_image.url
        if about.about_image:
            ctx["profile_src"] = BASE_URL + about.about_image.url
    # Browser preview: same portrait as the live site, as a plain URL.
    portrait_path, portrait_url = _portrait_file()
    if portrait_path:
        ctx["portrait_src"] = BASE_URL + portrait_url
    return ctx


def _wa_number(phone):
    """Digits-only WhatsApp number; Nigerian local formats (0xxx) -> international (234xxx)."""
    if not phone:
        return ""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if digits.startswith("0"):
        digits = "234" + digits[1:]
    return digits


def send_contact_notification(contact):
    """Notify King Greatman Spirit about a new contact form lead."""
    send_html_email(
        subject=f"New Lead: {contact.full_name or 'Visitor'} — {contact.email or 'no email'}",
        template_name="emails/contact_notification_email.html",
        context={
            "contact": contact,
            "wa_phone": _wa_number(contact.phone_number),
        },
        to_list=[settings.EMAIL_HOST_USER],
        reply_to=[contact.email] if contact.email else None,
    )


def send_contact_confirmation(contact):
    """Auto-reply to the visitor who filled the contact form."""
    if not contact.email:
        return
    send_html_email(
        subject="We've received your message ✨ | King Greatman Spirit",
        template_name="emails/contact_confirmation_email.html",
        context={"contact": contact},
        to_list=[contact.email],
    )


def send_newsletter_confirmation(subscriber, unsubscribe_url=""):
    """Welcome email to a new newsletter subscriber."""
    send_html_email(
        subject="You're in! 🎉 Welcome to King Greatman Spirit's newsletter",
        template_name="emails/newsletter_confirmation_email.html",
        context={
            "subscriber": subscriber,
            "unsubscribe_url": unsubscribe_url,
        },
        to_list=[subscriber.email],
    )


def send_payment_receipt(payment):
    """Receipt email for a confirmed payment."""
    send_html_email(
        subject=f"Payment Received — Thank You! 💰 | King Greatman Spirit",
        template_name="emails/payment_receipt_email.html",
        context={"payment": payment},
        to_list=[payment.email],
    )
