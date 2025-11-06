from django.urls import path
from . import views

app_name = 'project_notes'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/create/', views.job_create, name='job_create'),
    path('job/<str:job_number>/', views.job_detail, name='job_detail'),
    path('job/<str:job_number>/edit/', views.job_edit, name='job_edit'),
    path('job/<str:job_number>/delete/', views.job_delete, name='job_delete'),
    path('job/<str:job_number>/add-note/', views.add_note, name='add_note'),
    path('note/<int:note_id>/edit/', views.edit_note, name='edit_note'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('equipment-note/<int:equipment_note_id>/edit/', views.edit_equipment_note, name='edit_equipment_note'),
    path('equipment-note/<int:equipment_note_id>/delete/', views.delete_equipment_note, name='delete_equipment_note'),
    path('kom/<int:kom_pk>/save-equipment/', views.save_equipment_line_items, name='save_equipment_line_items'),
]

