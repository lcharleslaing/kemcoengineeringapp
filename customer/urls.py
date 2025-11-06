from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('kom/', views.kom_list, name='kom_list'),
    path('kom/import/', views.kom_import, name='kom_import'),
    path('kom/<int:pk>/', views.kom_detail, name='kom_detail'),
    path('kom/<int:pk>/delete/', views.kom_delete, name='kom_delete'),
    path('kom/<int:pk>/export/', views.kom_export_text, name='kom_export_text'),
    path('kom/<int:pk>/open/', views.kom_open_file, name='kom_open_file'),
    path('kom/<int:pk1>/compare/<int:pk2>/', views.kom_compare, name='kom_compare'),
]

