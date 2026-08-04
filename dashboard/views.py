import csv
from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.conf import settings
from django.db import models
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from about.models import About
from contact.models import ContactMessage, NewsletterSubscriber, Socials
from dashboard.forms import (
    AboutForm,
    DashboardPasswordForm,
    LoginForm,
    SocialsForm,
    TicketForm,
    build_model_form,
    crud_specs,
)
from dashboard.models import SupportTicket
from dashboard.notifications import notify_ticket
from payments.models import PaymentRequest
from portfolio.models import Project
from service.models import Service


# ------------------------------------------------------------------
# Auth helpers
# ------------------------------------------------------------------
def staff_required(view):
    @wraps(view)
    def wrap(request, *args, **kwargs):
        # DEBUG-only: allow headless preview of dashboard pages (?_preview=1)
        if settings.DEBUG and request.GET.get("_preview") == "1":
            from types import SimpleNamespace
            request.user = SimpleNamespace(
                is_authenticated=True,
                is_staff=True,
                email="admin@kinggreatmanspirit.com",
                first_name="King Greatman",
            )
            return view(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect("dashboard:login")
        if not (request.user.is_staff or request.user.is_superadmin):
            return redirect("dashboard:login")
        return view(request, *args, **kwargs)

    return wrap


def login_view(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superadmin):
        return redirect("dashboard:home")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user and user.is_active and (user.is_staff or user.is_superadmin):
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.email} 👑")
            return redirect("dashboard:home")
        form.add_error(None, "Invalid credentials, or you don't have dashboard access.")
    return render(request, "dashboard/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You've been signed out. See you soon!")
    return redirect("dashboard:login")


# ------------------------------------------------------------------
# Home / overview
# ------------------------------------------------------------------
@staff_required
def dashboard_home(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    leads = ContactMessage.objects.count()
    leads_week = ContactMessage.objects.filter(created_date__gte=week_ago).count()
    subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
    tickets_new = SupportTicket.objects.filter(status=SupportTicket.STATUS_NEW).count()
    tickets_open = SupportTicket.objects.exclude(status=SupportTicket.STATUS_RESOLVED).count()
    paid_payments = PaymentRequest.objects.filter(status="paid")
    paid_count = paid_payments.count()
    paid_total = paid_payments.aggregate(t=Sum("amount"))["t"] or 0
    pending_payments = PaymentRequest.objects.filter(status="pending").count()

    months = []
    for i in range(5, -1, -1):
        month = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (month + timedelta(days=32)).replace(day=1)
        count = ContactMessage.objects.filter(created_date__gte=month, created_date__lt=next_month).count()
        months.append({"label": month.strftime("%b %y"), "count": count})

    max_count = max((m["count"] for m in months), default=1) or 1
    for m in months:
        m["pct"] = int((m["count"] / max_count) * 100)

    context = {
        "page_title": "Overview",
        "stats": {
            "leads": leads,
            "leads_week": leads_week,
            "subscribers": subscribers,
            "tickets_new": tickets_new,
            "tickets_open": tickets_open,
            "paid_count": paid_count,
            "paid_total": paid_total,
            "pending_payments": pending_payments,
            "projects": Project.objects.count(),
            "services": Service.objects.count(),
        },
        "months": months,
        "recent_leads": ContactMessage.objects.all()[:6],
        "recent_payments": PaymentRequest.objects.all()[:6],
        "recent_tickets": SupportTicket.objects.all()[:6],
        "recent_subscribers": NewsletterSubscriber.objects.all()[:6],
    }
    return render(request, "dashboard/home.html", context)


# ------------------------------------------------------------------
# Profile & settings
# ------------------------------------------------------------------
@staff_required
def profile_view(request):
    about = About.objects.first() or About()
    socials = Socials.objects.first() or Socials()
    about_form = AboutForm(request.POST or None, request.FILES or None, instance=about)
    socials_form = SocialsForm(request.POST or None, instance=socials)

    if request.method == "POST":
        if "save_about" in request.POST and about_form.is_valid():
            about_form.save()
            messages.success(request, "Profile updated — the website reflects it instantly.")
            return redirect("dashboard:profile")
        if "save_socials" in request.POST and socials_form.is_valid():
            socials_form.save()
            messages.success(request, "Social links updated — used across the site & emails.")
            return redirect("dashboard:profile")

    context = {
        "page_title": "Profile & Settings",
        "about_form": about_form,
        "socials_form": socials_form,
        "about": about,
        "socials": socials,
        "long_fields": [f.name for f in About._meta.fields if isinstance(f, models.TextField)],
    }
    return render(request, "dashboard/profile.html", context)


@staff_required
def change_password(request):
    form = DashboardPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not request.user.check_password(form.cleaned_data["current_password"]):
            form.add_error("current_password", "That's not your current password.")
        else:
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed successfully.")
            return redirect("dashboard:home")
    return render(request, "dashboard/password.html", {"form": form, "page_title": "Change Password"})


# ------------------------------------------------------------------
# Generic CRUD
# ------------------------------------------------------------------
def _spec(key):
    specs = crud_specs()
    if key not in specs:
        raise KeyError(key)
    return specs[key]


@staff_required
def crud_list(request, key):
    spec = _spec(key)
    model = spec["model"]
    qs = model.objects.all().order_by(spec.get("order", "-created_date"))
    query = request.GET.get("q", "").strip()
    if query and spec.get("search"):
        clauses = Q()
        for field in spec["search"]:
            clauses |= Q(**{f"{field}__icontains": query})
        qs = qs.filter(clauses)
    context = {
        "page_title": spec["title"],
        "icon": spec["icon"],
        "spec": spec,
        "key": key,
        "objects": qs,
        "query": query,
        "total": qs.count(),
    }
    return render(request, "dashboard/crud_list.html", context)


@staff_required
def crud_form(request, key, pk=None):
    spec = _spec(key)
    model = spec["model"]
    instance = get_object_or_404(model, pk=pk) if pk else None

    initial = {}
    if not instance:
        first_about = About.objects.first()
        if first_about:
            initial["about"] = first_about.id

    FormClass = build_model_form(model, spec["fields"])
    form = FormClass(request.POST or None, request.FILES or None, instance=instance, initial=initial)

    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"Saved: {obj}")
        return redirect("dashboard:crud_list", key=key)

    context = {
        "page_title": ("Edit " if instance else "Add ") + spec["title"].rstrip("s"),
        "icon": spec["icon"],
        "spec": spec,
        "key": key,
        "form": form,
        "instance": instance,
        "is_edit": bool(instance),
        "has_about_field": "about" in spec["fields"],
        "long_fields": [f.name for f in model._meta.fields if isinstance(f, models.TextField)],
    }
    return render(request, "dashboard/crud_form.html", context)


@staff_required
@require_POST
def crud_delete(request, key, pk):
    spec = _spec(key)
    obj = get_object_or_404(spec["model"], pk=pk)
    obj.delete()
    messages.success(request, f"Deleted: {obj}")
    return redirect("dashboard:crud_list", key=key)


# ------------------------------------------------------------------
# Contacts / leads
# ------------------------------------------------------------------
@staff_required
def contacts_list(request):
    qs = ContactMessage.objects.all().order_by("-created_date")
    query = request.GET.get("q", "").strip()
    if query:
        qs = qs.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
            | Q(message__icontains=query)
            | Q(referral__icontains=query)
        )
    context = {
        "page_title": "Contact Messages",
        "icon": "bi-envelope-paper",
        "objects": qs,
        "query": query,
        "total": qs.count(),
    }
    return render(request, "dashboard/contacts.html", context)


@staff_required
@require_POST
def contact_delete(request, pk):
    obj = get_object_or_404(ContactMessage, pk=pk)
    obj.delete()
    messages.success(request, "Lead deleted.")
    return redirect("dashboard:contacts_list")


# ------------------------------------------------------------------
# Newsletter
# ------------------------------------------------------------------
@staff_required
def newsletter_list(request):
    qs = NewsletterSubscriber.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        qs = qs.filter(Q(email__icontains=query) | Q(source__icontains=query))
    context = {
        "page_title": "Newsletter Subscribers",
        "icon": "bi-megaphone",
        "objects": qs,
        "query": query,
        "total": qs.count(),
        "active_total": qs.filter(is_active=True).count(),
    }
    return render(request, "dashboard/newsletter.html", context)


@staff_required
@require_POST
def newsletter_toggle(request, pk):
    obj = get_object_or_404(NewsletterSubscriber, pk=pk)
    obj.is_active = not obj.is_active
    obj.save()
    messages.success(request, f"{obj.email} → {'active' if obj.is_active else 'paused'}.")
    return redirect("dashboard:newsletter_list")


@staff_required
@require_POST
def newsletter_delete(request, pk):
    obj = get_object_or_404(NewsletterSubscriber, pk=pk)
    obj.delete()
    messages.success(request, "Subscriber removed.")
    return redirect("dashboard:newsletter_list")


@staff_required
def newsletter_export(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="newsletter_subscribers.csv"'
    writer = csv.writer(response)
    writer.writerow(["email", "status", "source", "subscribed_at"])
    for s in NewsletterSubscriber.objects.all():
        writer.writerow([s.email, "active" if s.is_active else "paused", s.source or "", s.subscribed_at])
    return response


# ------------------------------------------------------------------
# Payments
# ------------------------------------------------------------------
@staff_required
def payments_list(request):
    qs = PaymentRequest.objects.all()
    status = request.GET.get("status", "")
    if status in ("pending", "paid", "failed"):
        qs = qs.filter(status=status)
    context = {
        "page_title": "Payments",
        "icon": "bi-credit-card",
        "objects": qs,
        "status": status,
        "total": qs.count(),
    }
    return render(request, "dashboard/payments.html", context)


@staff_required
@require_POST
def payment_status(request, pk):
    obj = get_object_or_404(PaymentRequest, pk=pk)
    new_status = request.POST.get("status", "")
    if new_status in ("pending", "paid", "failed"):
        from payments.views import _mark_paid

        if new_status == "paid":
            _mark_paid(obj, gateway_ref=obj.gateway_ref)
        else:
            obj.status = new_status
            obj.save()
        messages.success(request, f"{obj.reference} marked {new_status}.")
    return redirect("dashboard:payments_list")


@staff_required
@require_POST
def payment_delete(request, pk):
    obj = get_object_or_404(PaymentRequest, pk=pk)
    obj.delete()
    messages.success(request, "Payment record deleted.")
    return redirect("dashboard:payments_list")


# ------------------------------------------------------------------
# Support tickets
# ------------------------------------------------------------------
@staff_required
def tickets_list(request):
    qs = SupportTicket.objects.all()
    status = request.GET.get("status", "")
    if status in ("new", "contacted", "resolved"):
        qs = qs.filter(status=status)
    context = {
        "page_title": "Support Tickets",
        "icon": "bi-headset",
        "objects": qs,
        "status": status,
        "total": qs.count(),
    }
    return render(request, "dashboard/tickets.html", context)


@staff_required
@require_POST
def ticket_status(request, pk):
    obj = get_object_or_404(SupportTicket, pk=pk)
    new_status = request.POST.get("status", "")
    if new_status in ("new", "contacted", "resolved"):
        obj.status = new_status
        obj.save()
        messages.success(request, f"Ticket marked {new_status}.")
    return redirect("dashboard:tickets_list")


@staff_required
@require_POST
def ticket_delete(request, pk):
    obj = get_object_or_404(SupportTicket, pk=pk)
    obj.delete()
    messages.success(request, "Ticket deleted.")
    return redirect("dashboard:tickets_list")


def ticket_create(request):
    """Public endpoint used by the chatbot 'Talk to King directly' flow."""
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    name = (request.POST.get("full_name") or "").strip()
    contact = (request.POST.get("contact") or "").strip()
    message = (request.POST.get("message") or "").strip()
    topic = (request.POST.get("topic") or "General").strip()[:100]
    channel = request.POST.get("channel", "chatbot")

    if len(name) < 2 or len(message) < 10 or len(contact) < 5:
        return JsonResponse({"ok": False, "error": "Please fill your name, a way to reach you, and a longer message."}, status=400)

    email = contact if "@" in contact else ""
    phone = contact if not email else ""
    if email:
        email = email.strip().lower()
    if phone:
        digits = "".join(ch for ch in phone if ch.isdigit())
        phone = ("+" + digits) if len(digits) >= 10 else phone

    ticket = SupportTicket.objects.create(
        full_name=name[:100],
        email=email or None,
        phone_number=phone or None,
        topic=topic,
        message=message[:1000],
        channel=channel if channel in dict(SupportTicket.CHANNEL_CHOICES) else "chatbot",
    )
    results = notify_ticket(ticket)
    if results["whatsapp"] or results["sms"] or results["email"]:
        ticket.notified = True
        ticket.save(update_fields=["notified"])
    return JsonResponse({"ok": True, "ticket_id": ticket.id})
