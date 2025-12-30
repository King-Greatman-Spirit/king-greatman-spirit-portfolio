from django.contrib import admin
from .models import Summary, Education, Experience

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'about')
    list_filter = ('about',)

class EducationAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'institution', 'about')
    list_filter = ('about',)

class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'year', 'about')
    list_filter = ('about',)

admin.site.register(Summary, SummaryAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Experience, ExperienceAdmin)
