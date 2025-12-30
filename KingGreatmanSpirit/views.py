from django.shortcuts import render
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
    }
    
    return render(request, 'home.html', context)
