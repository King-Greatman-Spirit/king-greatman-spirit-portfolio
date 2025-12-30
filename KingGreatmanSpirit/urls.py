from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chaining/', include('smart_selects.urls')),
    path('', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('about/', include('about.urls')),
    path('resume/', include('resume.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('service/', include('service.urls')),
    path('contact/', include('contact.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
