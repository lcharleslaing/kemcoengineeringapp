from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Dashboard
    path('', views.resources_dashboard, name='dashboard'),
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/update/', views.department_update, name='department_update'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Roles
    path('roles/', views.role_list, name='role_list'),
    path('roles/<int:pk>/', views.role_detail, name='role_detail'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/update/', views.role_update, name='role_update'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),
    
    # People
    path('people/', views.person_list, name='person_list'),
    path('people/<int:pk>/', views.person_detail, name='person_detail'),
    path('people/create/', views.person_create, name='person_create'),
    path('people/<int:pk>/update/', views.person_update, name='person_update'),
    path('people/<int:pk>/delete/', views.person_delete, name='person_delete'),
]

