import uuid

from django.db import models
from service.models import Service

PAYMENT_METHODS = (
    ('flutterwave', 'Flutterwave (Cards, Bank Transfer, USSD, Mobile Money)'),
    ('paystack', 'Paystack (Cards, Bank Transfer, USSD)'),
    ('binance', 'Binance Pay (Crypto)'),
)

PAYMENT_STATUS = (
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
)

CURRENCIES = (
    ('NGN', 'NGN — Nigerian Naira (₦)'),
    ('USD', 'USD — US Dollar ($)'),
    ('GBP', 'GBP — British Pound (£)'),
    ('EUR', 'EUR — Euro (€)'),
    ('JPY', 'JPY — Japanese Yen (¥)'),
    ('CAD', 'CAD — Canadian Dollar (C$)'),
    ('AUD', 'AUD — Australian Dollar (A$)'),
    ('GHS', 'GHS — Ghanaian Cedi (GH₵)'),
    ('KES', 'KES — Kenyan Shilling (KSh)'),
    ('ZAR', 'ZAR — South African Rand (R)'),
)


class PaymentRequest(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField(max_length=120)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='NGN')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference = models.CharField(max_length=100, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    gateway_ref = models.CharField(max_length=200, blank=True, null=True)
    gateway_response = models.TextField(blank=True, null=True)
    paid_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "KGS-" + uuid.uuid4().hex[:20].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} — {self.currency} {self.amount} ({self.status})"

    class Meta:
        ordering = ("-created_date",)
