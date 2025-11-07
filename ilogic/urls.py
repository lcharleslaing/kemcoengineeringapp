from django.urls import path
from . import views

app_name = 'ilogic'

urlpatterns = [
    # Assembly views
    path('', views.assembly_list, name='assembly_list'),
    path('assembly/create/', views.assembly_create, name='assembly_create'),
    path('assembly/<int:pk>/', views.assembly_detail, name='assembly_detail'),
    path('assembly/<int:pk>/edit/', views.assembly_edit, name='assembly_edit'),
    path('assembly/<int:pk>/delete/', views.assembly_delete, name='assembly_delete'),
    
    # Component views
    path('component/<int:pk>/', views.component_detail, name='component_detail'),
    path('component/<int:pk>/edit/', views.component_edit, name='component_edit'),
    path('component/<int:pk>/delete/', views.component_delete, name='component_delete'),
    
    # Rule views
    path('rule/<int:pk>/', views.rule_detail, name='rule_detail'),
    path('rule/<int:pk>/edit/', views.rule_edit, name='rule_edit'),
    path('rule/<int:pk>/delete/', views.rule_delete, name='rule_delete'),
    path('rule/<int:pk>/analyze/', views.rule_analyze, name='rule_analyze'),
    
    # Import views
    path('import/structured/', views.import_structured, name='import_structured'),
    path('import/markdown/', views.import_markdown, name='import_markdown'),
    path('import/paste/', views.import_paste, name='import_paste'),
    
    # Analysis views
    path('analysis/', views.analysis_dashboard, name='analysis_dashboard'),
    path('analysis/assembly/<int:pk>/', views.assembly_analysis, name='assembly_analysis'),
    
    # Inconsistency views
    path('inconsistencies/', views.inconsistency_list, name='inconsistency_list'),
    path('inconsistency/<int:pk>/', views.inconsistency_detail, name='inconsistency_detail'),
    path('inconsistency/<int:pk>/fix/', views.inconsistency_fix, name='inconsistency_fix'),
    
    # Configurator views
    path('configurator/', views.configurator_list, name='configurator_list'),
    path('configurator/create/', views.configurator_create, name='configurator_create'),
    path('configurator/<int:pk>/', views.configurator_detail, name='configurator_detail'),
    path('configurator/<int:pk>/simulate/', views.configurator_simulate, name='configurator_simulate'),
]

