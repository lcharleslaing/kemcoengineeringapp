from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Event
from .utils import CalendarHelper, WeekCalendarHelper, DayCalendarHelper


class EventModelTest(TestCase):
    """Test cases for Event model"""

    def setUp(self):
        """Set up test user and event"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.start = timezone.now()
        self.end = self.start + timedelta(hours=2)

    def test_event_creation(self):
        """Test creating a valid event"""
        event = Event.objects.create(
            user=self.user,
            title='Test Event',
            start_datetime=self.start,
            end_datetime=self.end,
            description='Test description',
            location='Test location'
        )
        
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.description, 'Test description')
        self.assertEqual(event.location, 'Test location')

    def test_event_string_representation(self):
        """Test __str__ method"""
        event = Event.objects.create(
            user=self.user,
            title='Test Event',
            start_datetime=self.start,
            end_datetime=self.end
        )
        
        expected = f"Test Event ({self.start.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(event), expected)

    def test_event_validation_end_before_start(self):
        """Test that end_datetime must be after start_datetime"""
        with self.assertRaises(ValidationError):
            event = Event(
                user=self.user,
                title='Invalid Event',
                start_datetime=self.end,
                end_datetime=self.start  # End before start - invalid
            )
            event.save()

    def test_event_duration(self):
        """Test duration property"""
        event = Event.objects.create(
            user=self.user,
            title='Test Event',
            start_datetime=self.start,
            end_datetime=self.end
        )
        
        self.assertEqual(event.duration, timedelta(hours=2))

    def test_event_is_past(self):
        """Test is_past property"""
        past_event = Event.objects.create(
            user=self.user,
            title='Past Event',
            start_datetime=timezone.now() - timedelta(days=2),
            end_datetime=timezone.now() - timedelta(days=2, hours=-1)
        )
        
        self.assertTrue(past_event.is_past)

    def test_event_is_upcoming(self):
        """Test is_upcoming property"""
        future_event = Event.objects.create(
            user=self.user,
            title='Future Event',
            start_datetime=timezone.now() + timedelta(days=2),
            end_datetime=timezone.now() + timedelta(days=2, hours=1)
        )
        
        self.assertTrue(future_event.is_upcoming)

    def test_event_overlaps_with(self):
        """Test overlaps_with method"""
        event1 = Event.objects.create(
            user=self.user,
            title='Event 1',
            start_datetime=self.start,
            end_datetime=self.end
        )
        
        # Overlapping event
        event2 = Event.objects.create(
            user=self.user,
            title='Event 2',
            start_datetime=self.start + timedelta(hours=1),
            end_datetime=self.end + timedelta(hours=1)
        )
        
        self.assertTrue(event1.overlaps_with(event2))
        
        # Non-overlapping event
        event3 = Event.objects.create(
            user=self.user,
            title='Event 3',
            start_datetime=self.end + timedelta(hours=1),
            end_datetime=self.end + timedelta(hours=3)
        )
        
        self.assertFalse(event1.overlaps_with(event3))


class CalendarViewsTest(TestCase):
    """Test cases for calendar views"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test event
        self.event = Event.objects.create(
            user=self.user,
            title='Test Event',
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=1)
        )

    def test_month_view_requires_login(self):
        """Test that month view requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('calendar_month'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_month_view_authenticated(self):
        """Test month view with authenticated user"""
        response = self.client.get(reverse('calendar_month'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Calendar')

    def test_week_view_authenticated(self):
        """Test week view with authenticated user"""
        response = self.client.get(reverse('calendar_week'))
        self.assertEqual(response.status_code, 200)

    def test_day_view_authenticated(self):
        """Test day view with authenticated user"""
        response = self.client.get(reverse('calendar_day'))
        self.assertEqual(response.status_code, 200)

    def test_event_list_view(self):
        """Test event list view"""
        response = self.client.get(reverse('event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_event_detail_view(self):
        """Test event detail view"""
        response = self.client.get(reverse('event_detail', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_event_create_view_get(self):
        """Test GET request to event create view"""
        response = self.client.get(reverse('event_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Event')

    def test_event_create_view_post(self):
        """Test POST request to create an event"""
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        data = {
            'title': 'New Event',
            'start_datetime': start.strftime('%Y-%m-%dT%H:%M'),
            'end_datetime': end.strftime('%Y-%m-%dT%H:%M'),
            'description': 'New event description',
            'location': 'Test location'
        }
        
        response = self.client.post(reverse('event_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify event was created
        self.assertTrue(Event.objects.filter(title='New Event').exists())

    def test_event_update_view(self):
        """Test event update view"""
        response = self.client.get(reverse('event_update', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Event')

    def test_event_delete_view(self):
        """Test event delete view"""
        response = self.client.get(reverse('event_delete', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Event')

    def test_event_export_ics(self):
        """Test ICS export"""
        response = self.client.get(reverse('event_export_ics', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar')
        self.assertIn('BEGIN:VCALENDAR', response.content.decode())

    def test_user_can_only_see_own_events(self):
        """Test that users can only see their own events"""
        # Create another user and event
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        other_event = Event.objects.create(
            user=other_user,
            title='Other User Event',
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=1)
        )
        
        # Try to access other user's event
        response = self.client.get(reverse('event_detail', kwargs={'pk': other_event.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden


class CalendarUtilsTest(TestCase):
    """Test cases for calendar utility functions"""

    def test_calendar_helper_month_calendar(self):
        """Test CalendarHelper generates correct month calendar"""
        helper = CalendarHelper(2025, 1)  # January 2025
        weeks = helper.get_month_calendar()
        
        self.assertIsInstance(weeks, list)
        self.assertTrue(len(weeks) >= 4)  # At least 4 weeks in a month

    def test_calendar_helper_navigation(self):
        """Test month navigation"""
        helper = CalendarHelper(2025, 1)
        
        prev_year, prev_month = helper.prev_month()
        self.assertEqual(prev_year, 2024)
        self.assertEqual(prev_month, 12)
        
        next_year, next_month = helper.next_month()
        self.assertEqual(next_year, 2025)
        self.assertEqual(next_month, 2)

    def test_week_helper(self):
        """Test WeekCalendarHelper"""
        helper = WeekCalendarHelper(2025, 1)
        days = helper.get_week_days()
        
        self.assertEqual(len(days), 7)  # 7 days in a week

    def test_day_helper(self):
        """Test DayCalendarHelper"""
        helper = DayCalendarHelper(2025, 1, 15)
        hours = helper.get_hours()
        
        self.assertEqual(len(hours), 24)  # 24 hours in a day
        self.assertEqual(hours[0], 0)
        self.assertEqual(hours[-1], 23)
