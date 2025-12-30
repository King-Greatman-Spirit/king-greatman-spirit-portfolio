from .models import Service
from about.models import About

def menu_links(request):
    about = About.objects.all()[0]
    links =  Service.objects.filter(about=about)
    return dict(service_links=links)
