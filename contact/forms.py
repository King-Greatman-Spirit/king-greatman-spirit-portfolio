import re
from django import forms
from django.core.exceptions import ValidationError
from .models import ContactMessage, Socials


class ContactMessageForm(forms.ModelForm):

    class Meta:
        model = ContactMessage
        fields = [
            'full_name',
            'email',
            'phone_number',
            'company_name',
            'service',
            'channel',
            'message',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'full_name': 'Enter Full Name',
            'email': 'Enter Email Address',
            'phone_number': 'Enter Phone Number',
            'company_name': 'Enter Company Name',
            'service': 'Select Service You Are Interested In',
            'channel': 'Select How You Heard About Us',
            'message': 'Enter Message (20–500 characters)',
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': placeholder,
            })
            self.fields[field].widget.attrs['placeholder'] = placeholder

        # Select fields
        self.fields['channel'].widget.attrs['class'] = 'form-select'
        self.fields['service'].widget.attrs['class'] = 'form-select'
        self.fields['service'].empty_label = "Select Service You Are Interested In"

        # Textarea rows
        self.fields['message'].widget.attrs['rows'] = 4

    # ================= VALIDATIONS ================= #

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not re.match(r"^[A-Za-z\s'-]{3,}$", name):
            raise ValidationError("Please enter a valid full name.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            raise ValidationError("Please enter a valid email address.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone and not re.match(r"^\+?\d{10,15}$", phone):
            raise ValidationError("Please enter a valid phone number.")
        return phone

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()

        if len(message) < 20:
            raise ValidationError("Your message is too short. Please provide more details.")

        if re.search(r'(https?://|www\.)', message.lower()):
            raise ValidationError("Links are not allowed in the message.")

        spam_words = ["test", "asdf", "qwerty", "12345"]
        if any(word in message.lower() for word in spam_words):
            raise ValidationError("Please enter a meaningful message.")

        return message


class SocialsForm(forms.ModelForm):
    class Meta:
        model = Socials
        fields = '__all__'
