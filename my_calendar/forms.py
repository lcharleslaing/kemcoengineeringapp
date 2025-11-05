from django import forms
from django.core.exceptions import ValidationError
from .models import Event


class EventForm(forms.ModelForm):
    """Form for creating and editing events"""
    
    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'input input-bordered w-full'
            }
        ),
        label='Start Date & Time'
    )
    
    end_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'input input-bordered w-full'
            }
        ),
        label='End Date & Time'
    )

    class Meta:
        model = Event
        fields = ['title', 'start_datetime', 'end_datetime', 'description', 'location']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Event description (optional)'
            }),
            'location': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Event location (optional)'
            }),
        }

    def clean(self):
        """Validate that end_datetime is after start_datetime"""
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')

        if start and end:
            if end <= start:
                raise ValidationError('End time must be after start time.')

        return cleaned_data


class QuickEventForm(forms.ModelForm):
    """Simplified form for quickly creating events"""
    
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'input input-bordered w-full'
            }
        )
    )
    
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'input input-bordered w-full'
            }
        ),
        label='Start Time'
    )
    
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'input input-bordered w-full'
            }
        ),
        label='End Time'
    )

    class Meta:
        model = Event
        fields = ['title', 'location']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Event title'
            }),
            'location': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Location (optional)'
            }),
        }
