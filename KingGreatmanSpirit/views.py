from django.shortcuts import render
from django.views.defaults import page_not_found
from urllib.parse import urlparse
from service.models import Service
from portfolio.models import Project, ProjectImages, Testimonial
from contact.models import ContactMessage, CHANNEL_CHOICES


# ---------------------------------------------------------------
# client_sites()
# Builds the "Trusted by forward-thinking companies" marquee list.
# Every Project that has a real web URL becomes a marquee entry,
# so no client is ever skipped again (previously hardcoded with
# only 3 sites). Duplicate domains are removed.
# ---------------------------------------------------------------

# Real brand logos we host ourselves, keyed by site domain.
# (Google's favicon service has no entry for these domains, so the
# marquee used to show a broken image / wrong icon for them.)
LOCAL_LOGOS = {
    'kinggreatmanspirit.com': 'static/img/logo.png',          # our own KGS logo
    'preview.bgtechnical.info': 'media/testimonials/bgt_logo.png',  # real BGT logo
}

# Domains whose favicon is missing or an empty file, so Google's
# favicon service has nothing to show -> render a gold monogram
# badge (first letter of the company name) instead.
NO_FAVICON = {
    'piggingproducts.com',       # PPA - favicon.ico is an empty file
    'test.plan-ng.com',          # PLAN - preview site, no favicon
    'savvychemicalsltd.com',     # Savvy Chemicals - no favicon at all
}


def client_sites():
    """Every client with a live project URL, deduplicated by domain."""
    seen = set()     # Domains already added, to avoid duplicates.
    sites = []       # Final list of {'name', 'domain', 'logo', 'no_favicon'}.
    # Sort alphabetically by client name for a tidy marquee order.
    for project in Project.objects.all().order_by('client'):
        url = (project.project_url or '').strip()
        # Skip projects without a real website (e.g. Excel dashboards).
        if not url.startswith('http'):
            continue
        try:
            # Extract the domain, e.g. https://www.example.com/path -> example.com
            domain = urlparse(url).netloc.lower().replace('www.', '')
        except Exception:
            # Malformed URL - skip it rather than crash the page.
            continue
        if not domain or domain in seen:
            continue
        seen.add(domain)
        sites.append({
            'name': project.client or project.title,
            'domain': domain,
            'logo': LOCAL_LOGOS.get(domain, ''),     # local logo file, if any
            'no_favicon': domain in NO_FAVICON,      # no usable favicon online
        })
    return sites


def home(request):
    # Load the data needed by every section of the home page.
    services = Service.objects.select_related('about').order_by('-created_date')
    testimonials = Testimonial.objects.select_related('about').order_by('-created_date')
    contacts = ContactMessage.objects.all()
    projects = (
        Project.objects
        .select_related('service')               # Avoid N+1 queries for service names.
        .prefetch_related('project_images')      # Load all project screenshots in one query.
    )

    context = {
        'title': 'KGS Home',
        'services': services,
        'projects': projects,   # ✅ REQUIRED for displaying projects on home page
        'testimonials': testimonials,
        'contacts': contacts,
        'channel_choices': CHANNEL_CHOICES,
        # Marquee of all client websites, generated from the database.
        'client_sites': client_sites(),
    }
    
    return render(request, 'home.html', context)


def custom_404(request, exception):
    # Serve the custom 404 page instead of Django's default.
    return page_not_found(request, exception, template_name='404.html')
