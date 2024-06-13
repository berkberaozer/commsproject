from django import forms
from .models import User


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
