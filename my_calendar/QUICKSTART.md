# My Calendar - Quick Start Guide

## ?? Getting Started in 3 Steps

### Step 1: Run the Migration
```bash
python manage.py migrate my_calendar
```

### Step 2: Start Your Server
```bash
python manage.py runserver
# OR use your existing startup scripts:
./start_django.sh
```

### Step 3: Access the Calendar
Open your browser and navigate to:
- **Main Calendar**: http://127.0.0.1:8000/calendar/
- **From Dashboard**: Click "My Calendar" card on the dashboard

## ?? Quick Tour

### Creating Your First Event
1. Click the **"New Event"** button (top right)
2. Fill in:
   - **Title**: Name your event
   - **Start Date & Time**: When it begins
   - **End Date & Time**: When it ends
   - **Location** (optional): Where it happens
   - **Description** (optional): Additional details
3. Click **"Create Event"**

### Viewing Events

**Month View** (Default)
- See all events for the month in a grid
- Click any date's **+** button to add an event on that day
- Click an event chip to see details

**Week View**
- 7-day overview with event cards
- Great for planning your week

**Day View**
- Hourly breakdown of a single day
- Detailed schedule view

**List View**
- Paginated table of all events
- Sort and search capabilities

### Managing Events

**View Details**: Click any event
**Edit**: Click "Edit Event" button
**Delete**: Click "Delete Event" button (with confirmation)
**Export**: Click "Export to Calendar" for ICS file

## ?? Pro Tips

1. **Quick Add**: In month view, click the + button on any date to create an event pre-filled with that date

2. **Navigation**: Use Previous/Next buttons or the view tabs to move around

3. **Today Highlighting**: The current date is always highlighted with a border

4. **Status Badges**: Events show badges:
   - ?? **Today** - happening today
   - ?? **Upcoming** - in the future
   - ? **Past** - already happened

5. **ICS Export**: Download events as .ics files to import into:
   - Google Calendar
   - Apple Calendar
   - Outlook
   - Any ICS-compatible calendar app

## ?? Testing

Verify everything works:
```bash
python manage.py test my_calendar
```

Expected: **23 tests pass** ?

## ?? Common Tasks

### Add an all-day event
Set start time to 00:00 and end time to 23:59

### Schedule a meeting
1. Set precise start/end times
2. Add location (e.g., "Conference Room A")
3. Add attendee info in description

### Weekly review
Use Week View to see your upcoming 7 days at a glance

### Monthly planning
Use Month View to get a bird's-eye view of your schedule

## ?? Troubleshooting

**Can't see events?**
- Make sure you're logged in
- Events are user-specific - you only see your own events

**Form validation error?**
- End time must be after start time
- All required fields must be filled

**Time zone issues?**
- Check TIME_ZONE in settings.py
- All times are stored timezone-aware (UTC)

## ?? More Information

- **Full Documentation**: See `README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Django Admin**: Access at http://127.0.0.1:8000/admin/

## ? You're All Set!

The calendar is ready to use. Start creating events and managing your schedule!

---

**Need Help?** Check the comprehensive README.md for detailed information on all features.
