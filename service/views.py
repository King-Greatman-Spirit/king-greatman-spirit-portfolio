from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceProcess
from about.models import About


def service(request, slug):
    about = About.objects.first()
    services = Service.objects.select_related('about').order_by('-created_date')

    # Get ONE service by slug
    service = get_object_or_404(Service, about=about, slug=slug)

    title = f"Service: {service.name}"

    # Get processes linked to this service
    service_processes = ServiceProcess.objects.filter(
        about=about,
        service=service
    ).order_by('id')

    # Optional: aos animation delay
    service.aos_delay = 100

    context = {
        'title': title,
        'about': about,
        'services': services,
        'service': service,            # 👈 singular (recommended)
        'service_processes': service_processes,
    }

    return render(request, 'service/service.html', context)
