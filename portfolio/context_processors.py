from about.models import About
from service.models import Service
from .models import Project

def portfolio_links(request):
    """
    Provides global access to About, Services, and Projects for templates.
    """
    about = About.objects.first()
    service_ids = Project.objects.order_by('service').values_list('service', flat=True).distinct()
    services = Service.objects.filter(id__in=service_ids)
    projects = Project.objects.all()

    return {
        'about_links': about,
        'portfolio_services': services,
        'all_projects': projects,
    }
