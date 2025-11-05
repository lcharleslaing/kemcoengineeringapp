from django.urls import path
from . import views

urlpatterns = [
    # Calendar views
    path('', views.calendar_redirect, name='calendar_home'),
    path('month/', views.calendar_month_view, name='calendar_month'),
    path('month/<int:year>/<int:month>/', views.calendar_month_view, name='calendar_month'),
    path('week/', views.calendar_week_view, name='calendar_week'),
    path('week/<int:year>/<int:week>/', views.calendar_week_view, name='calendar_week'),
    path('day/', views.calendar_day_view, name='calendar_day'),
    path('day/<int:year>/<int:month>/<int:day>/', views.calendar_day_view, name='calendar_day'),
    
    # Event CRUD
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    
    # Export
    path('events/<int:pk>/export/', views.event_export_ics, name='event_export_ics'),
]
