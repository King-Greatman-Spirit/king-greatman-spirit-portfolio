from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectImages
from service.models import Service
from django.db.models import Count


def project_detail(request, project_slug):
    """Display details of a single project by slug"""
    project = get_object_or_404(Project, slug=project_slug)
    project_images = project.project_images.all()
    title = f"Project: {project.title}"

    context = {
        'project': project,
        'project_images': project_images,
        'title': title,
    }
    return render(request, 'portfolio/portfolio.html', context)

def service_projects(request, service_slug):
    service = get_object_or_404(Service, slug=service_slug)

    projects = (
        Project.objects
        .filter(service=service)
        .select_related('service')
        .prefetch_related('project_images')
    )

    portfolio_services = Service.objects.annotate(
        project_count=Count("project_set")
    ).filter(project_count__gt=0)

    services = Service.objects.all()

    context = {
        'projects': projects,
        'portfolio_services': portfolio_services,
        'services': services,   # ✅ REQUIRED
        'active_service': service,
        'title': f"{service.name} Projects",
    }

    return render(request, 'home.html', context)

def all_projects(request):
    """Display all projects together"""

    projects = (
        Project.objects
        .select_related('service')
        .prefetch_related('project_images')
        .order_by('service__name', 'id')  # ✅ THIS IS REQUIRED
    )

    portfolio_services = Service.objects.annotate(
        project_count=Count("project_set")
    ).filter(project_count__gt=0)

    context = {
        'projects': projects,
        'title': "All Projects",
        'portfolio_services': portfolio_services,
    }
    return render(request, 'home.html', context)