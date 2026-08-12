from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from .sitemaps import StaticViewSitemap, ProjectSitemap, ServiceSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "services": ServiceSitemap,
}

handler404 = "KingGreatmanSpirit.views.custom_404"

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
    path('payment/', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),

    # SEO
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production container (DEBUG=False, gunicorn): serve uploaded media
    # directly through Django + Whitenoise. Small-site, single-server setup.
    from django.views.static import serve as media_serve
    urlpatterns += [
        path('media/<path:path>', media_serve, {'document_root': settings.MEDIA_ROOT}),
    ]
