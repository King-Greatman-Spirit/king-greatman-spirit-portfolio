from django.db import models

class About(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    intro_text = models.TextField(max_length=500, blank=True, null=True)
    title = models.TextField(max_length=500, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)

    # Personal info
    birthday = models.CharField(max_length=50, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)

    phone1 = models.CharField(max_length=30, blank=True, null=True)
    phone2 = models.CharField(max_length=30, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    degree = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    freelance = models.CharField(max_length=50, blank=True, null=True)
    outro_text = models.TextField(max_length=500, blank=True, null=True)

    # Image fields
    profile_image = models.ImageField(upload_to='about_images/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='about_images/', blank=True, null=True)
    about_image = models.ImageField(upload_to='about_images/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        def format_phone(phone):
            if not phone:
                return phone
            num = ''.join(filter(str.isdigit, phone))
            if num.startswith("0"):
                num = "234" + num[1:]
            if len(num) >= 10:
                return f"+{num[:3]} ({num[3:6]}) {num[6:9]} {num[9:]}"
            return phone

        self.phone1 = format_phone(self.phone1)
        self.phone2 = format_phone(self.phone2)

        super().save(*args, **kwargs)

    def __str__(self):
        return "About Section"


class Statistic(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="stats")
    label = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    value = models.IntegerField()
    icon = models.CharField(max_length=100, help_text="Example: bi bi-emoji-smile", blank=True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label

class Skill(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100, blank=True, null=True)
    percentage = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

