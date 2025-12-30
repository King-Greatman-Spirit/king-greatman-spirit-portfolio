from .models import About
from resume.models import Summary, Education, Experience

def about_links(request):
    about = About.objects.first()  # single About instance or None
    skills = about.skills.all() if about else []
    stats = about.stats.all() if about else []
    summaries = about.summaries.all() if about else []
    educations = about.educations.all() if about else []
    experiences = about.experiences.all() if about else []

    return {
        'about_links': about,       # About instance
        'about_skills': skills,     # Skill queryset
        'about_stats': stats,       # Statistic queryset
        'summaries': summaries,     # Summary queryset
        'educations': educations,   # Education queryset
        'experiences': experiences, # Experience queryset
    }
