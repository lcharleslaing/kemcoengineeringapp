from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Event(models.Model):
    """Calendar event model with timezone-aware datetime fields"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='calendar_events',
        help_text="Event owner"
    )
    title = models.CharField(
        max_length=200,
        help_text="Event title (required)"
    )
    start_datetime = models.DateTimeField(
        help_text="Event start date and time"
    )
    end_datetime = models.DateTimeField(
        help_text="Event end date and time"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional event description"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional event location"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['user', 'start_datetime']),
            models.Index(fields=['start_datetime', 'end_datetime']),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_datetime.strftime('%Y-%m-%d %H:%M')})"

    def clean(self):
        """Validate that end_datetime is after start_datetime"""
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError({
                    'end_datetime': 'End time must be after start time.'
                })

    def save(self, *args, **kwargs):
        """Run validation before saving"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration(self):
        """Return event duration as timedelta"""
        return self.end_datetime - self.start_datetime

    @property
    def is_past(self):
        """Check if event is in the past"""
        return self.end_datetime < timezone.now()

    @property
    def is_today(self):
        """Check if event occurs today"""
        now = timezone.now()
        return (self.start_datetime.date() <= now.date() <= self.end_datetime.date())

    @property
    def is_upcoming(self):
        """Check if event is in the future"""
        return self.start_datetime > timezone.now()

    def overlaps_with(self, other_event):
        """Check if this event overlaps with another event"""
        return (
            self.start_datetime < other_event.end_datetime and
            self.end_datetime > other_event.start_datetime
        )
