from django.db import models
from django.core.validators import RegexValidator
from service.models import Service

# Validator for international phone numbers
phone_number_validator = RegexValidator(
    r'^\+?[0-9]{7,15}$',
    'Enter a valid phone number. It can start with + and contain 7 to 15 digits. Example: +12345678901'
)

# Choices for lead source
CHANNEL_CHOICES = (
    (0, 'How did you find us?'),
    ('Facebook','Facebook'),
    ('Instagram', 'Instagram'),
    ('LinkedIn', 'LinkedIn'),
    ('Threads', 'Threads'),
    ('Google','Google'),
    ('Youtube','Youtube'),
    ('Tiktok','Tiktok'),
    ('GitHub','GitHub'),
    ('Twitter','Twitter'),
    ('Referral','Referral'),
    ('Telegram','Telegram'),
    ('WhatsApp','WhatsApp'),
    ('Pinterest','Pinterest'),
    ('Others','Others'),
)

# Contact messages
class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[phone_number_validator]
    )
    company_name = models.CharField(max_length=50, blank=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    channel = models.CharField(max_length=100, choices=CHANNEL_CHOICES, default=0)
    message = models.TextField(max_length=500)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.full_name


# Social media links
class Socials(models.Model):
    platform = models.CharField(max_length=50, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    youTube = models.URLField(blank=True, null=True)
    telegram = models.URLField(blank=True, null=True)
    whatsapp = models.URLField(blank=True, null=True)
    tiktok = models.URLField(blank=True, null=True)
    threads = models.URLField(blank=True, null=True)
    linktree = models.URLField(blank=True, null=True)
    pinterest = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.platform or "Social Links"
    
    class Meta:
        verbose_name = 'socials'
        verbose_name_plural = 'socials'