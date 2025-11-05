from django.apps import AppConfig


class MyCalendarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "my_calendar"
    verbose_name = "My Calendar"
