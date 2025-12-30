from django.contrib import admin
from .models import ContactMessage, Socials

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'service', 'channel', 'created_date')
    list_filter = ('channel', 'service', 'created_date')
    search_fields = ('full_name', 'email', 'phone_number', 'company_name')
    readonly_fields = ('created_date', 'modified_date')

@admin.register(Socials)
class SocialsAdmin(admin.ModelAdmin):
    list_display = ('platform', 'facebook')
    search_fields = ('platform',)
