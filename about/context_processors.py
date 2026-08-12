from pathlib import Path

from django.conf import settings

from .models import About
from resume.models import Summary, Education, Experience, Certification, Achievement


def spiritual_image_url():
    """URL of the extra portrait (spiritual.png) if present, else the about image."""
    path = Path(settings.MEDIA_ROOT) / 'about_images' / 'spiritual.png'
    if path.exists():
        return f"{settings.MEDIA_URL}about_images/spiritual.png"
    about = About.objects.first()
    return about.about_image.url if about and about.about_image else ''


def portrait_image_url():
    """URL of the King Greatman Spirit portrait if present, else the spiritual image."""
    path = Path(settings.MEDIA_ROOT) / 'about_images' / 'king-greatman-spirit.png'
    if path.exists():
        return f"{settings.MEDIA_URL}about_images/king-greatman-spirit.png"
    return spiritual_image_url()


def about_links(request):
    about = About.objects.first()  # single About instance or None
    skills = about.skills.all() if about else []
    stats = about.stats.all() if about else []
    summaries = about.summaries.all() if about else []
    educations = about.educations.all() if about else []
    experiences = about.experiences.all() if about else []
    # Credentials (badge grid in Resume) - alphabetically sorted for a tidy grid.
    certifications = about.certifications.all().order_by('title') if about else []
    # Split into two groups: 14 credentials shown by default (the 6 professional
    # ones plus the first 8 co-curricular ones), and the remaining co-curricular
    # ones hidden behind a "Show more" toggle so the Resume stays compact.
    # Both groups keep the original alphabetical order.
    cocurricular_issuer = 'Co-Curricular Programming Center'
    professional_certs = [c for c in certifications if c.issuer != cocurricular_issuer]
    co_curricular_certs = [c for c in certifications if c.issuer == cocurricular_issuer]
    visible_certs = professional_certs + co_curricular_certs[:8]  # 14 shown
    hidden_certs = co_curricular_certs[8:]                        # the rest (14)
    # Impact milestone cards (Achievements section).
    achievements = about.achievements.all() if about else []

    return {
        'about_links': about,       # About instance
        'about_skills': skills,     # Skill queryset
        'about_stats': stats,       # Statistic queryset
        'summaries': summaries,     # Summary queryset
        'educations': educations,   # Education queryset
        'experiences': experiences, # Experience queryset
        'certifications': certifications,  # Certification queryset (all)
        'visible_certs': visible_certs,    # list (14 shown in the grid)
        'hidden_certs': hidden_certs,      # list (14 behind the toggle)
        'achievements': achievements,      # Achievement queryset
        'spiritual_image': spiritual_image_url(),
        'portrait_image': portrait_image_url(),
    }
