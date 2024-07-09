from django import forms
from .models import User
import re


class RegistrationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()

    def clean(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('Username already taken')
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError('Email already taken')
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise forms.ValidationError('Passwords do not match')
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", self.cleaned_data['password']):
            raise forms.ValidationError('Password length should be at least'
                                        ' eight characters, and it should contains'
                                        ' at least one letter, one number and one special character:')
        if not re.match("^[a-zA-Z0-9_-]*$", self.cleaned_data['username']):
            raise forms.ValidationError('Username must contain only English letters, numbers and hyphens.')
