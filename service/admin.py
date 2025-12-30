from django.contrib import admin
from .models import Service, ServiceProcess


# Inline admin for ServiceProcess (optional but recommended)
class ServiceProcessInline(admin.TabularInline):
    model = ServiceProcess
    extra = 1
    fields = ('name', 'description', 'image', 'service', 'about')
    autocomplete_fields = ['service', 'about']


# Service admin
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'acronym',
        'about',
        'created_date',
        'modified_date',
    )
    search_fields = (
        'name',
        'acronym',
        'description',
        'about__name',
    )
    list_filter = (
        'about',
        'created_date',
    )
    readonly_fields = ('acronym',)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceProcessInline]


# ServiceProcess admin
class ServiceProcessAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'service',
        'about',
        'created_date',
        'modified_date',
    )
    search_fields = (
        'name',
        'description',
        'service__name',
        'about__name',
    )
    list_filter = (
        'service',
        'about',
        'created_date',
    )
    autocomplete_fields = ['service', 'about']


# Register models
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceProcess, ServiceProcessAdmin)
