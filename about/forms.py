from django import forms
from .models import About, Skill, Statistic

class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields = [
            'name', 'intro_text', 'title', 'description', 'birthday', 'website',
            'phone1', 'phone2', 'city', 'age', 'degree', 'email', 'freelance', 'outro_text',
            'profile_image', 'cover_image', 'about_image'
        ]

    def __init__(self, *args, **kwargs):
        super(AboutForm, self).__init__(*args, **kwargs)
        placeholders = {
            'name': 'Enter Full Name',
            'intro_text': 'Enter Introduction Text',
            'title': 'Enter Your Title',
            'description': 'Enter Description',
            'birthday': 'Enter Birthday (e.g., 01 Jan 1990)',
            'website': 'Enter Website URL',
            'phone1': 'Enter Primary Phone Number',
            'phone2': 'Enter Secondary Phone Number',
            'city': 'Enter City',
            'age': 'Enter Age',
            'degree': 'Enter Highest Degree',
            'email': 'Enter Email Address',
            'freelance': 'Freelance Status (Available/Not Available)',
            'outro_text': 'Enter Outro Text',
            'profile_image': 'Upload Profile Image',
            'cover_image': 'Upload Cover Image',
            'about_image': 'Upload About Image',
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'
            if isinstance(self.fields[field], forms.CharField):
                self.fields[field].widget.attrs['maxlength'] = self.fields[field].max_length
            if isinstance(self.fields[field], forms.IntegerField):
                self.fields[field].widget.attrs['min'] = 0

        # Add file input class for images
        self.fields['profile_image'].widget.attrs['class'] += ' form-control-file'
        self.fields['cover_image'].widget.attrs['class'] += ' form-control-file'
        self.fields['about_image'].widget.attrs['class'] += ' form-control-file'


class StatisticForm(forms.ModelForm):
    class Meta:
        model = Statistic
        fields = ['about', 'label', 'description', 'value', 'icon']

    def __init__(self, *args, **kwargs):
        super(StatisticForm, self).__init__(*args, **kwargs)
        self.fields['about'].empty_label = 'Select About Section'
        self.fields['about'].widget.attrs['class'] = 'form-control'

        placeholders = {
            'label': 'Enter Statistic Label (e.g. Thrilled Clients)',
            'description': 'Enter Short Description',
            'value': 'Enter Statistic Number (e.g. 232)',
            'icon': 'Enter Bootstrap Icon Class (e.g. bi bi-emoji-smile)',
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['about', 'name', 'percentage']

    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__(*args, **kwargs)
        self.fields['about'].empty_label = 'Select About Section'
        self.fields['about'].widget.attrs['class'] = 'form-control'
        placeholders = {
            'name': 'Enter Skill Name',
            'percentage': 'Enter Skill Proficiency (%)',
        }
        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'
            if field == 'percentage':
                self.fields[field].widget.attrs['min'] = 0
                self.fields[field].widget.attrs['max'] = 100
