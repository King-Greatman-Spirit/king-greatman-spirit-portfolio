from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control'
    }), required=False)  # Password is optional for updates

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-control'
    }), required=False)  # Confirm password is optional

    image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password', 'image']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'Enter First Name',
            'last_name': 'Enter Last Name',
            'phone_number': 'Enter Phone Number',
            'email': 'Enter Email Address',
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # If updating details and password is left blank, do not change it
        if not password and self.instance.pk:
            cleaned_data['password'] = self.instance.password  # Keep existing password

        # Validate password match only if a new password is provided
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Password does not match!')

        return cleaned_data

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        password = self.cleaned_data.get('password')

        # If a new password is provided, hash and update it
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user
