from django.contrib import admin
from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone_number", "topic", "channel", "status", "notified", "created_date")
    list_filter = ("status", "channel", "notified")
    search_fields = ("full_name", "email", "phone_number", "message", "topic")
