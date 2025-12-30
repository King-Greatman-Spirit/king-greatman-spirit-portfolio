from django import forms
from .models import Project, ProjectImages, Testimonial

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['about', 'service', 'title', 'project_scope', 'client', 'industry', 'project_url', 'completion_date']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Title'}),
            'project_scope': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'client': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Industry'}),
            'project_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project URL'}),
            'completion_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

class ProjectImagesForm(forms.ModelForm):
    class Meta:
        model = ProjectImages
        fields = ['about', 'service', 'project', 'image', 'name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
        }

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['about', 'full_name', 'role', 'company_name', 'weblink', 'message', 'image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Role'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'weblink': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WebLink Name'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
        }
