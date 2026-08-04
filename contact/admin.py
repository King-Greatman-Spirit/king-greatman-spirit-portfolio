from django.contrib import admin
from .models import ContactMessage, Socials, NewsletterSubscriber

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'service', 'channel', 'referral', 'created_date')
    list_filter = ('channel', 'service', 'referral', 'created_date')
    search_fields = ('full_name', 'email', 'phone_number', 'company_name', 'referral')
    readonly_fields = ('created_date', 'modified_date')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'source', 'subscribed_at')
    list_filter = ('is_active', 'source', 'subscribed_at')
    search_fields = ('email', 'source')
    readonly_fields = ('subscribed_at',)

@admin.register(Socials)
class SocialsAdmin(admin.ModelAdmin):
    list_display = ('platform', 'facebook')
    search_fields = ('platform',)
