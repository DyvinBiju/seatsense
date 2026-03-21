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
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'auditorium': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'speakers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['duration'].required = False
        self.fields['speakers'].required = False
        
        # Ensure all other fields have required attribute for browser validation
        for field_name in self.fields:
            if field_name not in ['duration', 'speakers']:
                self.fields[field_name].required = True

    def clean(self):
        cleaned_data = super().clean()
        auditorium = cleaned_data.get('auditorium')
        event_date = cleaned_data.get('event_date')
        event_time = cleaned_data.get('event_time')
        new_duration_str = cleaned_data.get('duration')

        def parse_duration(d_str):
            if not d_str: return 2.0 # Default fallback
            s = str(d_str).lower()
            if 'full' in s and 'day' in s: return 12.0
            import re
            nums = re.findall(r'(\d+(\.\d+)?)', s)
            if nums:
                val = float(nums[0][0])
                if 'min' in s: return val / 60.0
                if 'day' in s: return val * 24.0
                return val
            return 2.0

        if auditorium and event_date and event_time:
            from datetime import datetime, timedelta
            
            new_start = datetime.combine(event_date, event_time)
            new_dur_hours = parse_duration(new_duration_str)
            new_end = new_start + timedelta(hours=new_dur_hours)
            
            existing_events = Event.objects.filter(auditorium=auditorium, event_date=event_date)
            
            if self.instance.pk:
                existing_events = existing_events.exclude(pk=self.instance.pk)
            
            for existing in existing_events:
                existing_start = datetime.combine(existing.event_date, existing.event_time)
                existing_dur_hours = parse_duration(existing.duration)
                existing_end = existing_start + timedelta(hours=existing_dur_hours)
                
                min_start_after = existing_end + timedelta(hours=2)
                max_end_before = existing_start - timedelta(hours=2)
                
                # Check if New Event overlaps with the 'Blocked Out' time slot
                if new_start < min_start_after and new_end > max_end_before:
                    raise forms.ValidationError(
                        f"Warning: '{existing.title}' is scheduled from {existing_start.strftime('%I:%M %p')} "
                        f"to approx. {existing_end.strftime('%I:%M %p')} in this venue. "
                        f"Please allow at least a 2-hour buffer before or after it."
                    )
        
        return cleaned_data

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
