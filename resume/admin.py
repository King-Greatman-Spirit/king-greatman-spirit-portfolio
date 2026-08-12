from django.contrib import admin
from .models import Summary, Education, Experience, Certification, Achievement


# ---------------------------------------------------------------
# Admin registration for all Resume models.
# Each class customises how the model looks in the Django admin
# (which columns are shown in the list view, filters, search).
# ---------------------------------------------------------------

class SummaryAdmin(admin.ModelAdmin):
    # Columns shown in the admin list view for the Summary model.
    list_display = ('full_name', 'phone', 'email', 'about')
    # Sidebar filter so rows can be narrowed by the About profile.
    list_filter = ('about',)

class EducationAdmin(admin.ModelAdmin):
    # Columns shown in the admin list view for the Education model.
    list_display = ('title', 'year', 'institution', 'about')
    list_filter = ('about',)

class ExperienceAdmin(admin.ModelAdmin):
    # Columns shown in the admin list view for the Experience model.
    list_display = ('title', 'company', 'year', 'about')
    list_filter = ('about',)

class CertificationAdmin(admin.ModelAdmin):
    # Columns + search for the Certification model (credentials grid).
    list_display = ('title', 'issuer', 'year', 'about')
    list_filter = ('about',)
    search_fields = ('title', 'issuer')

class AchievementAdmin(admin.ModelAdmin):
    # Columns for the Achievement model (impact milestone cards).
    list_display = ('label', 'description', 'about')
    list_filter = ('about',)

# Register every admin class with the Django admin site.
admin.site.register(Summary, SummaryAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Achievement, AchievementAdmin)
