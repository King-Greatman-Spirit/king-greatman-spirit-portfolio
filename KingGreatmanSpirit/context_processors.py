from django.conf import settings


def site_config(request):
    """Expose SEO/analytics config to all templates."""
    return {
        "GOOGLE_SITE_VERIFICATION": getattr(settings, "GOOGLE_SITE_VERIFICATION", ""),
        "GA4_MEASUREMENT_ID": getattr(settings, "GA4_MEASUREMENT_ID", ""),
    }
