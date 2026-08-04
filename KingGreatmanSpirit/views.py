from django.shortcuts import render
from django.views.defaults import page_not_found
from service.models import Service
from portfolio.models import Project, ProjectImages, Testimonial
from contact.models import ContactMessage, CHANNEL_CHOICES

def home(request):
    services = Service.objects.select_related('about').order_by('-created_date')
    testimonials = Testimonial.objects.select_related('about').order_by('-created_date')
    contacts = ContactMessage.objects.all()
    projects = (
        Project.objects
        .select_related('service')
        .prefetch_related('project_images')
    )

    context = {
        'title': 'KGS Home',
        'services': services,
        'projects': projects,   # ✅ REQUIRED for displaying projects on home page
        'testimonials': testimonials,
        'contacts': contacts,
        'channel_choices': CHANNEL_CHOICES,
        'client_sites': [
            {'name': 'PLAN-NG', 'domain': 'plan-ng.com'},
            {'name': 'Zhehus Group', 'domain': 'zhehusgroup.com'},
            {'name': 'Daikoo Energy', 'domain': 'daikooenergy.com'},
        ],
    }
    
    return render(request, 'home.html', context)

def custom_404(request, exception):
    return page_not_found(request, exception, template_name='404.html')
