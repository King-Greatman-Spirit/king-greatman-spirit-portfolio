from django import forms
from .models import Service, ServiceProcess
from about.models import About


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        # Added `acronym` to the form so it can be displayed (read-only)
        fields = ['about', 'name', 'acronym', 'slug', 'description', 'icon', 'image']

    def __init__(self, about, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)

        placeholders = {
            'name': 'Enter Service Name',
            'description': 'Describe Service',
            'icon': 'Enter Bootstrap Icon Class (e.g., bi bi-tools)',
            'image': 'Upload Image',
        }

        # Restrict `about` field to the current About instance
        # This prevents accidental assignment to another profile
        self.fields['about'].empty_label = 'Select About'
        self.fields['about'].queryset = About.objects.filter(id=about.id)
        self.fields['about'].widget.attrs['class'] = 'form-control'

        # Slug is auto-generated from the service name in the model
        # Marked as readonly to avoid manual edits
        self.fields['slug'].widget.attrs['readonly'] = 'readonly'
        self.fields['slug'].widget.attrs['class'] = 'form-control'

        # Acronym is auto-generated from the service name in the model
        # Displayed for clarity but not editable by the user
        self.fields['acronym'].widget.attrs['readonly'] = 'readonly'
        self.fields['acronym'].widget.attrs['class'] = 'form-control'
        self.fields['acronym'].widget.attrs['placeholder'] = 'Auto-generated'

        # Apply placeholders and Bootstrap classes to remaining fields
        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'

        # Improve textarea appearance
        self.fields['description'].widget.attrs['rows'] = 3



class ServiceProcessForm(forms.ModelForm):
    class Meta:
        model = ServiceProcess
        fields = ['about', 'service', 'name', 'description', 'image']

    # Initialize form fields with placeholders and classes
    def __init__(self, about, *args, **kwargs):
        super(ServiceProcessForm, self).__init__(*args, **kwargs)
        placeholders = {
            'name': 'Enter Process Name',
            'description': 'Describe Process',
            'image': 'Upload Image',
        }

        # Set custom queryset for the 'about' field
        self.fields['about'].empty_label = 'Select about'
        self.fields['about'].queryset = About.objects.filter(id=about.id)
        self.fields['about'].widget.attrs['class'] = 'form-control'

        # Set custom queryset for the 'service' field
        self.fields['service'].empty_label = 'Select Service'
        self.fields['service'].widget.attrs['class'] = 'form-control'

        # Apply placeholders and classes for other fields
        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'

        # Specific attributes for the 'description' field
        self.fields['description'].widget.attrs['rows'] = 3

