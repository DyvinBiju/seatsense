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

from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date', 'event_time', 'auditorium', 'category', 'ticket_price', 'image', 'duration', 'speakers']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'event_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write event details...'}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price in ₹'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2 Hours'}),
            'auditorium': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'speakers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
