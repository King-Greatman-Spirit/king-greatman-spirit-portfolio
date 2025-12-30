from django.contrib import admin
from .models import About,Statistic, Skill

# Inline for Statistics
class StatisticInline(admin.TabularInline):
    model = Statistic
    extra = 1
    fields = ('label', 'description', 'value', 'icon', 'created_date', 'modified_date')
    readonly_fields = ('created_date', 'modified_date')

# Inline for Skills
class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1  # Number of empty skill forms to display
    fields = ('name', 'percentage', 'created_date', 'modified_date')
    readonly_fields = ('created_date', 'modified_date')

# About Admin
class AboutAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'city', 'created_date', 'modified_date')
    search_fields = ('name', 'email', 'city')
    list_filter = ('city', 'created_date', 'modified_date')
    inlines = [SkillInline, StatisticInline]
    readonly_fields = ('created_date', 'modified_date')
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'intro_text', 'title', 'description', 'outro_text')
        }),
        ('Contact Info', {
            'fields': ('birthday', 'website', 'phone1', 'phone2', 'email', 'city', 'age', 'degree', 'freelance')
        }),
        ('Images', {
            'fields': ('profile_image', 'cover_image', 'about_image')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'modified_date')
        }),
    )

# Statistic Admin (optional standalone)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'icon', 'created_date', 'modified_date')
    search_fields = ('label', 'description', 'icon')
    list_filter = ('label', 'created_date')

# Skill Admin (optional standalone)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'about', 'percentage', 'created_date', 'modified_date')
    list_filter = ('about',)
    search_fields = ('name',)

# Register models
admin.site.register(About, AboutAdmin)
admin.site.register(Statistic, StatisticAdmin)
admin.site.register(Skill, SkillAdmin)
