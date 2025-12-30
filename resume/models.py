from django.db import models
from about.models import About

class Summary(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="summaries")
    full_name = models.CharField(max_length=100, blank=True, null=True)
    intro_text = models.TextField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    # Use phone1 and email from About model
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Default to About's phone/email if empty09014155705
        if self.about:
            if not self.phone:
                self.phone = self.about.phone1
            if not self.email:
                self.email = self.about.email
        super().save(*args, **kwargs)

    def __str__(self):
        return "Summary Section"
    
    class Meta:
        verbose_name = 'summary'
        verbose_name_plural = 'summaries'


class Education(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="educations")
    title = models.CharField(max_length=200, blank=True, null=True)
    year = models.CharField(max_length=50, blank=True, null=True)
    institution = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or "Education"


class Experience(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="experiences")
    title = models.CharField(max_length=200, blank=True, null=True)
    year = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    desc_one = models.TextField(blank=True, null=True)
    desc_two = models.TextField(blank=True, null=True)
    desc_three = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or "Experience"
