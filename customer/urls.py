from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('kom/', views.kom_list, name='kom_list'),
    path('kom/import/', views.kom_import, name='kom_import'),
    path('kom/<int:pk>/', views.kom_detail, name='kom_detail'),
]

