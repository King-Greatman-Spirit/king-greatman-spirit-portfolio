from django.db import models


class SupportTicket(models.Model):
    """A request to talk to a real human — created from the chatbot
    "Talk to King directly" flow, then alerted via WhatsApp / SMS / email."""

    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_RESOLVED = "resolved"

    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_RESOLVED, "Resolved"),
    )

    CHANNEL_CHOICES = (
        ("chatbot", "Website Chatbot"),
        ("site", "Website"),
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
    )

    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    topic = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(max_length=1000)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="chatbot")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    notified = models.BooleanField(default=False, help_text="Whether the owner was alerted (WhatsApp/SMS/email).")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_date",)

    def __str__(self):
        return f"Ticket by {self.full_name} ({self.status})"
