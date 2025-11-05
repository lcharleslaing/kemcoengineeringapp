# My Calendar - Django Calendar Application

A full-featured calendar application built with Django, featuring month, week, and day views with complete CRUD operations for events.

## Features

### Calendar Views
- **Month View**: Grid-based calendar showing all events in a month
- **Week View**: Detailed week view with events organized by day
- **Day View**: Hourly breakdown of a single day with all events
- **List View**: Paginated list of all events

### Event Management
- Create, Read, Update, Delete (CRUD) operations
- Event fields:
  - Title (required)
  - Start date/time (required)
  - End date/time (required)
  - Description (optional)
  - Location (optional)
  - Auto-tracked created/updated timestamps
- Form validation (end time must be after start time)
- Timezone-aware datetime handling

### Additional Features
- ICS export for individual events (import into Google Calendar, Outlook, etc.)
- Event status indicators (today, upcoming, past)
- Event overlap detection
- Responsive design using Tailwind CSS + DaisyUI
- User-specific events (users only see their own events)
- Django admin integration
- Comprehensive test suite

## Installation & Setup

### 1. Database Migration

The migrations have already been created. Run the migration to create the Event table:

```bash
python manage.py migrate my_calendar
```

### 2. Create a Superuser (if not done already)

```bash
python manage.py createsuperuser
```

### 3. Run Tests

Verify everything is working correctly:

```bash
python manage.py test my_calendar
```

## Usage

### Accessing the Calendar

Once your Django server is running, navigate to:

- Main calendar: `http://127.0.0.1:8000/calendar/`
- Month view: `http://127.0.0.1:8000/calendar/month/`
- Week view: `http://127.0.0.1:8000/calendar/week/`
- Day view: `http://127.0.0.1:8000/calendar/day/`
- Event list: `http://127.0.0.1:8000/calendar/events/`

### Creating Events

1. Click the "New Event" button in the calendar header
2. Fill in the event details (title, start/end times, optional description and location)
3. Click "Create Event"

**Quick Add**: Click the "+" button on any date in the month view to pre-fill that date

### Viewing Events

- In **Month View**: Events appear as chips on their respective dates
- In **Week View**: Events are displayed in cards for each day
- In **Day View**: Events are listed with full details and shown in an hourly grid
- Click any event to see its full details

### Editing Events

1. Navigate to the event detail page
2. Click "Edit Event"
3. Update the fields and save

### Deleting Events

1. Navigate to the event detail page
2. Click "Delete Event"
3. Confirm the deletion

### Exporting Events

From the event detail page, click "Export to Calendar" to download an ICS file that can be imported into:
- Google Calendar
- Apple Calendar
- Outlook
- Any calendar app supporting ICS format

## Project Structure

```
my_calendar/
??? migrations/
?   ??? 0001_initial.py          # Event model migration
?   ??? __init__.py
??? templates/
?   ??? my_calendar/
?       ??? base_calendar.html    # Base template with navigation
?       ??? month_view.html       # Month calendar grid
?       ??? week_view.html        # Week view with daily cards
?       ??? day_view.html         # Day view with hourly breakdown
?       ??? event_list.html       # Paginated event list
?       ??? event_detail.html     # Event details page
?       ??? event_form.html       # Create/edit event form
?       ??? event_confirm_delete.html  # Delete confirmation
??? templatetags/
?   ??? __init__.py
?   ??? calendar_filters.py       # Custom template filters
??? __init__.py
??? admin.py                      # Django admin configuration
??? apps.py                       # App configuration
??? forms.py                      # Event forms
??? models.py                     # Event model
??? tests.py                      # Comprehensive test suite
??? urls.py                       # URL routing
??? utils.py                      # Calendar helper utilities
??? views.py                      # View logic
??? README.md                     # This file
```

## Models

### Event

Main model for calendar events:

```python
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Properties**:
- `duration`: Returns event duration as timedelta
- `is_past`: Boolean indicating if event has ended
- `is_today`: Boolean indicating if event occurs today
- `is_upcoming`: Boolean indicating if event is in the future

**Methods**:
- `overlaps_with(other_event)`: Check if this event overlaps with another

## URL Routes

All routes are prefixed with `/calendar/`:

| Route | Name | Description |
|-------|------|-------------|
| `/calendar/` | calendar_home | Redirects to current month |
| `/calendar/month/` | calendar_month | Current month view |
| `/calendar/month/<year>/<month>/` | calendar_month | Specific month view |
| `/calendar/week/` | calendar_week | Current week view |
| `/calendar/week/<year>/<week>/` | calendar_week | Specific week view |
| `/calendar/day/` | calendar_day | Current day view |
| `/calendar/day/<year>/<month>/<day>/` | calendar_day | Specific day view |
| `/calendar/events/` | event_list | List all events |
| `/calendar/events/create/` | event_create | Create new event |
| `/calendar/events/<pk>/` | event_detail | View event details |
| `/calendar/events/<pk>/edit/` | event_update | Edit event |
| `/calendar/events/<pk>/delete/` | event_delete | Delete event |
| `/calendar/events/<pk>/export/` | event_export_ics | Export event as ICS |

## Utilities

The `utils.py` module provides helper classes for calendar generation:

- **CalendarHelper**: Generate month calendars with navigation
- **WeekCalendarHelper**: Generate week calendars with ISO week numbers
- **DayCalendarHelper**: Generate day views with hourly breakdowns
- **get_events_by_date()**: Group events by date
- **get_overlapping_events()**: Identify overlapping events
- **format_event_time()**: Format event times for display

## Admin Interface

Access the Django admin at `/admin/` to manage events with:
- List display with sorting and filtering
- Search by title, description, location, and username
- Date hierarchy for easy navigation
- Optimized queries with select_related

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test my_calendar

# Run with verbose output
python manage.py test my_calendar --verbosity 2

# Run specific test class
python manage.py test my_calendar.tests.EventModelTest
```

**Test Coverage**:
- Event model validation
- Event properties (is_past, is_upcoming, etc.)
- Event overlap detection
- All calendar views (authentication, rendering)
- CRUD operations
- User permission checks
- Calendar utility functions
- ICS export functionality

## Styling

The calendar uses **Tailwind CSS** and **DaisyUI** for modern, responsive design:
- Mobile-friendly responsive grid layouts
- Clean, professional UI components
- Consistent color scheme with theme support
- Hover effects and smooth transitions
- Icon integration using SVG

## Future Enhancements

Potential features to add:
- Event categories/tags
- Recurring events
- Event reminders/notifications
- Sharing events with other users
- Calendar subscriptions
- Multiple calendar views
- Event search and filtering
- Drag-and-drop event rescheduling
- Integration with external calendars (Google Calendar, Outlook)

## Troubleshooting

### Events not showing up
- Ensure you're logged in
- Check that events belong to your user account
- Verify the date range of the view

### Time zone issues
- Check `TIME_ZONE` setting in `settings.py`
- Ensure `USE_TZ = True` for timezone-aware datetimes

### Form validation errors
- End time must be after start time
- All required fields must be filled (title, start_datetime, end_datetime)

## License

This calendar application is part of the larger Django project and follows the same license.

## Support

For issues or questions, refer to the main project documentation or contact the development team.
