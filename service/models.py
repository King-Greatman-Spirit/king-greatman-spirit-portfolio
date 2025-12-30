import re
from django.db import models
from about.models import About
from smart_selects.db_fields import ChainedForeignKey
from django.urls import reverse
from django.utils.text import slugify


class Service(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=100, unique=True)
    acronym = models.CharField(max_length=20, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class")
    image = models.ImageField(upload_to='photos/services', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def generate_acronym(self):
        """
        Generates acronym from service name.
        Example:
        Tech Training & Prompt Engineering -> TT&P
        Artificial Intelligence & Machine Learning -> AI&ML
        """
        parts = re.split(r'(\s+|&)', self.name)
        acronym = ""

        for part in parts:
            part = part.strip()
            if part == "&":
                acronym += "&"
            elif part:
                acronym += part[0].upper()

        return acronym

    def save(self, *args, **kwargs):
        # Always generate slug from name
        self.slug = slugify(self.name, allow_unicode=True)

        # Always regenerate acronym from name
        self.acronym = self.generate_acronym()

        super().save(*args, **kwargs)

    def update_url(self):
        return reverse('update_service', args=[self.id])

    def delete_url(self):
        return reverse('delete_service', args=[self.id])

    def service_url(self):
        return reverse('service_slug', args=[self.slug])

    def __str__(self):
        return f"{self.name} ({self.acronym})"


class ServiceProcess(models.Model):
    about = models.ForeignKey(
        About, 
        on_delete=models.CASCADE, 
        related_name="service_processes"
    )
    service = ChainedForeignKey(
        Service,
        chained_field="about",
        chained_model_field="about",
        show_all=False,
        auto_choose=True,
        default=None)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='photos/service_process', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def update_url(self):
        return reverse('update_service_process', args=[self.id])

    def delete_url(self):
        return reverse('delete_service_process', args=[self.id])

    class Meta:
        verbose_name = 'Service Process'
        verbose_name_plural = 'Service Processes'

    def __str__(self):
        return self.name