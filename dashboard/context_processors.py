from about.models import About
from dashboard.models import SupportTicket


def dashboard_globals(request):
    """Extra context for dashboard templates."""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superadmin)):
        return {}
    return {
        "about_links": About.objects.first(),
        "tickets_new_count": SupportTicket.objects.filter(status=SupportTicket.STATUS_NEW).count(),
    }
