from django import forms
from .models import Summary, Education, Experience

class SummaryForm(forms.ModelForm):
    class Meta:
        model = Summary
        fields = [
          'about', 'full_name', 
          'intro_text', 'description', 'address',
          'phone', 'email'
        ]

    def __init__(self, *args, **kwargs):
        super(SummaryForm, self).__init__(*args, **kwargs)
        self.fields['about'].empty_label = 'Select About Section'
        self.fields['about'].widget.attrs['class'] = 'form-control'

        placeholders = {
            'full_name': 'Enter Full Name',
            'intro_text': 'Enter Introduction Text',
            'description': 'Enter Short Description',
            'address': 'Enter Address',
            'phone': 'Enter Phone Number',
            'email': 'Enter Email Address',
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
          'about', 'title', 'year', 
          'institution', 'description'
        ]

    def __init__(self, *args, **kwargs):
        super(EducationForm, self).__init__(*args, **kwargs)
        self.fields['about'].empty_label = 'Select About Section'
        self.fields['about'].widget.attrs['class'] = 'form-control'

        placeholders = {
            'title': 'Enter Title',
            'year': 'Enter Year',
            'institution': 'Enter Institution',
            'description': 'Enter Short Description',
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
          'about', 'title', 'year', 
          'company', 'city', 'desc_one',
          'desc_two', 'desc_three'
        ]

    def __init__(self, *args, **kwargs):
        super(ExperienceForm, self).__init__(*args, **kwargs)
        self.fields['about'].empty_label = 'Select About Section'
        self.fields['about'].widget.attrs['class'] = 'form-control'

        placeholders = {
            'title': 'Enter Title',
            'year': 'Enter Year',
            'company': 'Enter Company',
            'city': 'Enter City',
            'desc_one': 'Enter Description One',
            'desc_two': 'Enter Description Two',
            'desc_three': 'Enter Description Three',
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'
