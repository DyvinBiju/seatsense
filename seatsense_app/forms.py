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

from .models import Category, Speaker, Auditorium

class AuditoriumForm(forms.ModelForm):
    class Meta:
        model = Auditorium
        fields = ['name', 'location', 'total_rows', 'seats_per_row']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auditorium Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'total_rows': forms.NumberInput(attrs={'class': 'form-control', 'min': 8, 'max': 26}),
            'seats_per_row': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 15}),
        }

    def clean_total_rows(self):
        rows = self.cleaned_data.get('total_rows')
        if rows < 8:
            raise forms.ValidationError("Minimum 8 rows required for a proper theater experience.")
        if rows > 26:
            raise forms.ValidationError("Maximum 26 rows (A-Z) allowed.")
        return rows

    def clean_seats_per_row(self):
        seats = self.cleaned_data.get('seats_per_row')
        if seats < 10:
            raise forms.ValidationError("Minimum 10 seats per row required for a balanced grid.")
        if seats > 15:
            raise forms.ValidationError("Maximum 15 seats per row allowed.")
        return seats

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
        }

class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = ['name', 'designation', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Speaker Name'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Speaker Designation'}),
        }
