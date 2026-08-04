from django import forms
from django.db import models
from about.models import About, Statistic, Skill
from resume.models import Summary, Education, Experience
from portfolio.models import Project, ProjectImages, Testimonial
from service.models import Service, ServiceProcess
from contact.models import Socials
from dashboard.models import SupportTicket


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Your password", "autocomplete": "current-password"})
    )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("email") or not cleaned.get("password"):
            raise forms.ValidationError("Enter your email and password.")
        return cleaned


class DashboardPasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="At least 8 characters.",
    )
    confirm_new = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password") and cleaned.get("confirm_new") and cleaned["new_password"] != cleaned["confirm_new"]:
            raise forms.ValidationError("The two new passwords do not match.")
        return cleaned


class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields = [
            "name", "intro_text", "title", "description", "birthday", "website",
            "phone1", "phone2", "city", "age", "degree", "email", "freelance",
            "outro_text", "profile_image", "cover_image", "about_image",
        ]
        widgets = {
            "intro_text": forms.Textarea(attrs={"rows": 2}),
            "title": forms.Textarea(attrs={"rows": 2}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "outro_text": forms.Textarea(attrs={"rows": 2}),
        }


class SocialsForm(forms.ModelForm):
    class Meta:
        model = Socials
        fields = [
            "platform", "facebook", "twitter", "instagram", "linkedin", "github",
            "youTube", "telegram", "whatsapp", "tiktok", "threads", "linktree",
            "medium", "substack", "pinterest",
        ]


class TicketForm(forms.ModelForm):
    """Public form used by the chatbot handoff."""

    class Meta:
        model = SupportTicket
        fields = ["full_name", "email", "phone_number", "topic", "message", "channel"]
        widgets = {
            "topic": forms.HiddenInput(),
            "channel": forms.HiddenInput(),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name", "").strip()
        return name

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower() or None
        return email

    def clean_phone_number(self):
        phone = (self.cleaned_data.get("phone_number") or "").strip()
        if phone:
            digits = "".join(ch for ch in phone if ch.isdigit())
            return "+" + digits if len(digits) >= 10 else phone
        return None


# ------------------------------------------------------------------
# Generic model form factory for dashboard CRUD
# ------------------------------------------------------------------
TEXTAREA_FIELDS = {
    "description", "intro_text", "title", "message", "project_scope",
    "outro_text", "address", "desc_one", "desc_two", "desc_three",
}

CHAINED_FIELDS = {"service"}


def build_model_form(model, fields):
    """Build a ModelForm with sensible widgets for dashboard use."""
    widgets = {}
    labels = {}
    for name in fields:
        field = model._meta.get_field(name)
        if name in TEXTAREA_FIELDS:
            widgets[name] = forms.Textarea(attrs={"rows": 3})
        if isinstance(field, models.DateTimeField) and name == "completion_date":
            widgets[name] = forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            )
        if name == "message":
            widgets[name] = forms.Textarea(attrs={"rows": 4, "maxlength": 500})
        if name in CHAINED_FIELDS:
            widgets[name] = forms.Select()
        if name == "about":
            widgets[name] = forms.HiddenInput()
            labels[name] = ""

    meta = type("Meta", (), {
        "model": model,
        "fields": fields,
        "widgets": widgets,
        "labels": labels,
    })
    form_class = type("DashboardModelForm", (forms.ModelForm,), {"Meta": meta})

    for name in CHAINED_FIELDS:
        if name in fields:
            field = form_class.base_fields[name]
            field.queryset = Service.objects.all()

    return form_class


# ------------------------------------------------------------------
# CRUD registry — every content type editable from the dashboard
# ------------------------------------------------------------------
ABOUT_LABELS = {
    "title": "Intro line",
    "description": "Short description",
    "name": "Your name",
}


def crud_specs():
    return {
        "stats": {
            "title": "Statistics",
            "icon": "bi-graph-up-arrow",
            "model": Statistic,
            "fields": ["about", "label", "description", "value", "icon"],
            "cols": [("label", "Label", "text"), ("value", "Value", "number"), ("icon", "Icon", "code")],
            "search": ["label", "description"],
            "order": "label",
        },
        "skills": {
            "title": "Skills",
            "icon": "bi-patch-check",
            "model": Skill,
            "fields": ["about", "name", "percentage"],
            "cols": [("name", "Skill", "text"), ("percentage", "Level %", "number")],
            "search": ["name"],
            "order": "name",
        },
        "summaries": {
            "title": "Resume Summary",
            "icon": "bi-person-vcard",
            "model": Summary,
            "fields": ["about", "full_name", "intro_text", "description", "address", "phone", "email"],
            "cols": [("full_name", "Full name", "text"), ("phone", "Phone", "text"), ("email", "Email", "text")],
            "search": ["full_name", "email"],
            "order": "-created_date",
        },
        "educations": {
            "title": "Education",
            "icon": "bi-mortarboard",
            "model": Education,
            "fields": ["about", "title", "year", "institution", "description"],
            "cols": [("title", "Title", "text"), ("year", "Year", "text"), ("institution", "Institution", "text")],
            "search": ["title", "institution"],
            "order": "-year",
        },
        "experiences": {
            "title": "Experience",
            "icon": "bi-briefcase",
            "model": Experience,
            "fields": ["about", "title", "year", "company", "city", "desc_one", "desc_two", "desc_three"],
            "cols": [("title", "Role", "text"), ("company", "Company", "text"), ("year", "Year", "text"), ("city", "City", "text")],
            "search": ["title", "company"],
            "order": "-year",
        },
        "projects": {
            "title": "Projects",
            "icon": "bi-folder2-open",
            "model": Project,
            "fields": ["about", "service", "title", "project_scope", "client", "industry", "project_url", "completion_date"],
            "cols": [("title", "Title", "text"), ("client", "Client", "text"), ("industry", "Industry", "text"), ("completion_date", "Completed", "date")],
            "search": ["title", "client", "industry"],
            "order": "-created_date",
        },
        "project_images": {
            "title": "Project Images",
            "icon": "bi-images",
            "model": ProjectImages,
            "fields": ["about", "service", "project", "image", "name", "description"],
            "cols": [("image", "Image", "img"), ("project", "Project", "fk"), ("name", "Name", "text")],
            "search": ["name"],
            "order": "-created_date",
        },
        "services": {
            "title": "Services",
            "icon": "bi-stars",
            "model": Service,
            "fields": ["name", "description", "icon", "image"],
            "cols": [("name", "Name", "text"), ("acronym", "Acronym", "text"), ("image", "Icon image", "img")],
            "search": ["name", "description"],
            "order": "name",
        },
        "service_processes": {
            "title": "Service Process",
            "icon": "bi-diagram-3",
            "model": ServiceProcess,
            "fields": ["about", "service", "name", "description", "image"],
            "cols": [("name", "Step", "text"), ("service", "Service", "fk"), ("image", "Image", "img")],
            "search": ["name", "description"],
            "order": "name",
        },
        "testimonials": {
            "title": "Testimonials",
            "icon": "bi-chat-quote",
            "model": Testimonial,
            "fields": ["about", "full_name", "message", "role", "company_name", "weblink", "image"],
            "cols": [("full_name", "Client", "text"), ("company_name", "Company", "text"), ("image", "Photo", "img")],
            "search": ["full_name", "company_name"],
            "order": "-created_date",
        },
    }
