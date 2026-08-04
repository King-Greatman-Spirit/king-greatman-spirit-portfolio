from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from portfolio.models import Project
from service.models import Service


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return ["home"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.select_related("service").order_by("id")

    def location(self, obj):
        return obj.portfolio_url()

    def lastmod(self, obj):
        return obj.modified_date


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Service.objects.select_related("about").order_by("id")

    def location(self, obj):
        return reverse("service_slug", kwargs={"slug": obj.slug})

    def lastmod(self, obj):
        return obj.modified_date
