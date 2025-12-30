from django.contrib import admin
from .models import Project, ProjectImages, Testimonial

# Inline admin for ProjectImages
class ProjectImagesInline(admin.TabularInline):
    model = ProjectImages
    extra = 1  # How many extra blank forms
    fields = ('name', 'image', 'description', 'service', 'about')
    autocomplete_fields = ['service', 'about']

# Project admin
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'industry', 'about', 'service', 'created_date')
    prepopulated_fields = {"slug": ("title",)}  # Auto-generate slug from title
    inlines = [ProjectImagesInline]
    search_fields = ('title', 'service__name', 'about__name')
    list_filter = ('service', 'about', 'completion_date')

# ProjectImages admin
class ProjectImagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'about', 'service')
    search_fields = ('name', 'project__title', 'service__name', 'about__name')
    autocomplete_fields = ['project', 'service', 'about']

# Testimonial admin
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company_name', 'weblink', 'role', 'created_date')
    search_fields = ('full_name', 'company_name', 'weblink', 'role')
    list_filter = ('created_date',)

# Register models
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectImages, ProjectImagesAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
