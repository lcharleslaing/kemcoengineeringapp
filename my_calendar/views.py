from datetime import datetime, date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.decorators.http import require_http_methods

from .models import Event
from .forms import EventForm
from .utils import (
    CalendarHelper, 
    WeekCalendarHelper, 
    DayCalendarHelper,
    get_events_by_date,
    format_event_time
)


class EventOwnerMixin(UserPassesTestMixin):
    """Mixin to ensure user owns the event"""
    
    def test_func(self):
        event = self.get_object()
        return event.user == self.request.user


@login_required
def calendar_month_view(request, year=None, month=None):
    """Display month calendar view with events"""
    today = timezone.now()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    # Create calendar helper
    cal_helper = CalendarHelper(year, month)
    
    # Get events for this month
    start_date, end_date = cal_helper.get_month_bounds()
    events = Event.objects.filter(
        user=request.user,
        start_datetime__gte=start_date,
        start_datetime__lte=end_date
    ).order_by('start_datetime')

    # Group events by date
    events_by_date = get_events_by_date(events)

    # Get calendar weeks
    weeks = cal_helper.get_month_calendar()

    # Navigation
    prev_year, prev_month = cal_helper.prev_month()
    next_year, next_month = cal_helper.next_month()

    context = {
        'year': year,
        'month': month,
        'month_name': cal_helper.get_month_name(),
        'weeks': weeks,
        'weekday_abbr': cal_helper.get_weekday_abbr(),
        'events_by_date': events_by_date,
        'today': today.date(),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'view_type': 'month',
    }

    return render(request, 'my_calendar/month_view.html', context)


@login_required
def calendar_week_view(request, year=None, week=None):
    """Display week calendar view with events"""
    today = timezone.now()
    
    if not year or not week:
        iso_cal = today.isocalendar()
        year = iso_cal[0]
        week = iso_cal[1]
    else:
        year = int(year)
        week = int(week)

    # Create week helper
    week_helper = WeekCalendarHelper(year, week)
    
    # Get events for this week
    start_date, end_date = week_helper.get_week_bounds()
    events = Event.objects.filter(
        user=request.user,
        start_datetime__gte=start_date,
        start_datetime__lte=end_date
    ).order_by('start_datetime')

    # Group events by date
    events_by_date = get_events_by_date(events)

    # Get week days
    week_days = week_helper.get_week_days()

    # Navigation
    prev_year, prev_week = week_helper.prev_week()
    next_year, next_week = week_helper.next_week()

    context = {
        'year': year,
        'week': week,
        'week_days': week_days,
        'events_by_date': events_by_date,
        'today': today.date(),
        'prev_year': prev_year,
        'prev_week': prev_week,
        'next_year': next_year,
        'next_week': next_week,
        'format_event_time': format_event_time,
        'view_type': 'week',
    }

    return render(request, 'my_calendar/week_view.html', context)


@login_required
def calendar_day_view(request, year=None, month=None, day=None):
    """Display day calendar view with events"""
    today = timezone.now()
    
    if not year or not month or not day:
        year = today.year
        month = today.month
        day = today.day
    else:
        year = int(year)
        month = int(month)
        day = int(day)

    # Create day helper
    day_helper = DayCalendarHelper(year, month, day)
    
    # Get events for this day
    start_datetime, end_datetime = day_helper.get_day_bounds()
    events = Event.objects.filter(
        user=request.user,
        start_datetime__gte=start_datetime,
        start_datetime__lte=end_datetime
    ).order_by('start_datetime')

    # Get hours
    hours = day_helper.get_hours()

    # Navigation
    prev_year, prev_month, prev_day = day_helper.prev_day()
    next_year, next_month, next_day = day_helper.next_day()

    context = {
        'date': day_helper.date,
        'year': year,
        'month': month,
        'day': day,
        'events': events,
        'hours': hours,
        'today': today.date(),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'prev_day': prev_day,
        'next_year': next_year,
        'next_month': next_month,
        'next_day': next_day,
        'format_event_time': format_event_time,
        'view_type': 'day',
    }

    return render(request, 'my_calendar/day_view.html', context)


class EventListView(LoginRequiredMixin, ListView):
    """List all events for the logged-in user"""
    model = Event
    template_name = 'my_calendar/event_list.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user).order_by('-start_datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'list'
        return context


class EventDetailView(LoginRequiredMixin, EventOwnerMixin, DetailView):
    """Display event details"""
    model = Event
    template_name = 'my_calendar/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['format_event_time'] = format_event_time
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    """Create a new event"""
    model = Event
    form_class = EventForm
    template_name = 'my_calendar/event_form.html'
    
    def get_initial(self):
        """Pre-fill date/time if provided in query params"""
        initial = super().get_initial()
        
        date_str = self.request.GET.get('date')
        if date_str:
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                initial['start_datetime'] = datetime.combine(event_date, datetime.min.time())
                initial['end_datetime'] = datetime.combine(event_date, datetime.min.time())
            except ValueError:
                pass
        
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Event "{form.instance.title}" created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('calendar_month')


class EventUpdateView(LoginRequiredMixin, EventOwnerMixin, UpdateView):
    """Update an existing event"""
    model = Event
    form_class = EventForm
    template_name = 'my_calendar/event_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Event "{form.instance.title}" updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('event_detail', kwargs={'pk': self.object.pk})


class EventDeleteView(LoginRequiredMixin, EventOwnerMixin, DeleteView):
    """Delete an event"""
    model = Event
    template_name = 'my_calendar/event_confirm_delete.html'
    success_url = reverse_lazy('calendar_month')

    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        messages.success(request, f'Event "{event.title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
@require_http_methods(["GET"])
def event_export_ics(request, pk):
    """Export a single event as ICS file"""
    event = get_object_or_404(Event, pk=pk, user=request.user)
    
    # Generate ICS content
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//My Calendar//Event//EN
BEGIN:VEVENT
UID:{event.id}@mycalendar
DTSTAMP:{timezone.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{event.start_datetime.strftime('%Y%m%dT%H%M%S')}
DTEND:{event.end_datetime.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{event.title}
DESCRIPTION:{event.description or ''}
LOCATION:{event.location or ''}
END:VEVENT
END:VCALENDAR"""

    # Create response
    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="{event.title.replace(" ", "_")}.ics"'
    
    return response


@login_required
def calendar_redirect(request):
    """Redirect to current month view"""
    today = timezone.now()
    return redirect('calendar_month', year=today.year, month=today.month)
