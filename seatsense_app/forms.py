from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. A valid email address.')

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
