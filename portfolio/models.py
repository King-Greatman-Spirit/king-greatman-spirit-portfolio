from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from about.models import About
from service.models import Service
from django.urls import reverse
from django.utils.text import slugify

class Project(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="projects")
    service = ChainedForeignKey(
        Service,
        chained_field="about",
        chained_model_field="about",
        show_all=False,
        auto_choose=True,
        default=None
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    project_scope = models.TextField(max_length=1000)
    client = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    project_url = models.CharField(max_length=200, blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def portfolio_url(self):
        return reverse(
            "portfolio:project_detail",
            kwargs={"project_slug": self.slug}
        )

    def __str__(self):
        return self.title


class ProjectImages(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="project_images")
    service = ChainedForeignKey(
        Service,
        chained_field="about",
        chained_model_field="about",
        show_all=False,
        auto_choose=True,
        default=None
    )
    project = models.ForeignKey(Project, related_name="project_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/project', blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.title} Image"


class Testimonial(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="testimonials")
    full_name = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(max_length=500)
    role = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    weblink = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="testimonials/")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Testimonial by {self.full_name}"
