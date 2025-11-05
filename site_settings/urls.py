from django.urls import path

from . import views

app_name = "site_settings"

urlpatterns = [
    path("", views.site_settings_view, name="site_settings"),
]
