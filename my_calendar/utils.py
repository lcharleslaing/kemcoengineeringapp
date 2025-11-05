"""
Calendar utility functions for generating calendar structures
"""
import calendar
from datetime import datetime, timedelta, date, time
from django.utils import timezone


class CalendarHelper:
    """Helper class for generating calendar data structures"""
    
    def __init__(self, year=None, month=None):
        """Initialize with current year/month if not provided"""
        today = timezone.now()
        self.year = year if year else today.year
        self.month = month if month else today.month
        self.cal = calendar.monthcalendar(self.year, self.month)

    def get_month_calendar(self):
        """
        Return a list of weeks, where each week is a list of days.
        Days are represented as (day_number, date_object) tuples.
        Empty cells are (0, None).
        """
        weeks = []
        for week in self.cal:
            week_days = []
            for day in week:
                if day == 0:
                    week_days.append((0, None))
                else:
                    date_obj = date(self.year, self.month, day)
                    week_days.append((day, date_obj))
            weeks.append(week_days)
        return weeks

    def get_month_name(self):
        """Return full month name"""
        return calendar.month_name[self.month]

    def get_weekday_names(self):
        """Return list of weekday names"""
        return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    def get_weekday_abbr(self):
        """Return list of abbreviated weekday names"""
        return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def prev_month(self):
        """Return (year, month) tuple for previous month"""
        if self.month == 1:
            return (self.year - 1, 12)
        return (self.year, self.month - 1)

    def next_month(self):
        """Return (year, month) tuple for next month"""
        if self.month == 12:
            return (self.year + 1, 1)
        return (self.year, self.month + 1)

    def get_month_bounds(self):
        """Return start and end datetime for the month"""
        start = timezone.make_aware(datetime(self.year, self.month, 1, 0, 0, 0))
        
        # Last day of month
        last_day = calendar.monthrange(self.year, self.month)[1]
        end = timezone.make_aware(datetime(self.year, self.month, last_day, 23, 59, 59))
        
        return start, end


class WeekCalendarHelper:
    """Helper class for generating week view data"""
    
    def __init__(self, year, week_number):
        """Initialize with year and ISO week number"""
        self.year = year
        self.week_number = week_number
        
        # Get the first day of the week
        jan_1 = date(year, 1, 1)
        week_1_monday = jan_1 + timedelta(days=(1 - jan_1.isoweekday()))
        self.start_date = week_1_monday + timedelta(weeks=week_number - 1)

    def get_week_days(self):
        """Return list of dates for the week (Monday through Sunday)"""
        days = []
        for i in range(7):
            day = self.start_date + timedelta(days=i)
            days.append(day)
        return days

    def get_week_bounds(self):
        """Return start and end datetime for the week"""
        start = timezone.make_aware(datetime.combine(self.start_date, time.min))
        end_date = self.start_date + timedelta(days=6)
        end = timezone.make_aware(datetime.combine(end_date, time.max))
        return start, end

    def prev_week(self):
        """Return (year, week) tuple for previous week"""
        prev_date = self.start_date - timedelta(weeks=1)
        return (prev_date.isocalendar()[0], prev_date.isocalendar()[1])

    def next_week(self):
        """Return (year, week) tuple for next week"""
        next_date = self.start_date + timedelta(weeks=1)
        return (next_date.isocalendar()[0], next_date.isocalendar()[1])


class DayCalendarHelper:
    """Helper class for generating day view data"""
    
    def __init__(self, year, month, day):
        """Initialize with specific date"""
        self.date = date(year, month, day)
        self.year = year
        self.month = month
        self.day = day

    def get_day_bounds(self):
        """Return start and end datetime for the day"""
        start = timezone.make_aware(datetime.combine(self.date, time.min))
        end = timezone.make_aware(datetime.combine(self.date, time.max))
        return start, end

    def get_hours(self):
        """Return list of hours (0-23) for the day"""
        return list(range(24))

    def get_time_slots(self, interval=60):
        """
        Return list of time slots for the day
        interval: minutes per slot (default 60)
        """
        slots = []
        current = datetime.combine(self.date, time.min)
        end = datetime.combine(self.date, time.max)
        
        while current < end:
            slots.append(current.time())
            current += timedelta(minutes=interval)
        
        return slots

    def prev_day(self):
        """Return (year, month, day) tuple for previous day"""
        prev = self.date - timedelta(days=1)
        return (prev.year, prev.month, prev.day)

    def next_day(self):
        """Return (year, month, day) tuple for next day"""
        next_date = self.date + timedelta(days=1)
        return (next_date.year, next_date.month, next_date.day)


def get_events_by_date(events):
    """
    Group events by date
    Returns dict with date objects as keys and list of events as values
    """
    events_by_date = {}
    for event in events:
        event_date = event.start_datetime.date()
        if event_date not in events_by_date:
            events_by_date[event_date] = []
        events_by_date[event_date].append(event)
    return events_by_date


def get_overlapping_events(events):
    """
    Identify overlapping events in a list
    Returns list of tuples of overlapping event pairs
    """
    overlaps = []
    for i, event1 in enumerate(events):
        for event2 in events[i+1:]:
            if event1.overlaps_with(event2):
                overlaps.append((event1, event2))
    return overlaps


def format_event_time(event):
    """Format event time for display"""
    start = event.start_datetime
    end = event.end_datetime
    
    if start.date() == end.date():
        # Same day event
        return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"
    else:
        # Multi-day event
        return f"{start.strftime('%b %d, %I:%M %p')} - {end.strftime('%b %d, %I:%M %p')}"
