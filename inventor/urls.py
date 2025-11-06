from django.urls import path
from . import views

app_name = 'inventor'

urlpatterns = [
    path('', views.inventor_list, name='list'),
    path('open/<path:file_path_encoded>/', views.inventor_open_file, name='open_file'),
    path('open-location/<path:file_path_encoded>/', views.inventor_open_location, name='open_location'),
]

