from django.contrib import admin
from .models import PaymentRequest


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ('reference', 'full_name', 'email', 'amount', 'currency', 'method', 'status', 'paid_date', 'created_date')
    list_filter = ('status', 'method', 'currency', 'created_date')
    search_fields = ('reference', 'full_name', 'email', 'gateway_ref')
    readonly_fields = ('reference', 'created_date')
