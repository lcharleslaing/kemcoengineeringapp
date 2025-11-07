from django.urls import path
from . import views

app_name = 'sales_design'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]

