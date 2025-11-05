from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('api/chat/', views.chat_with_ai, name='chat_with_ai'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('apps/<slug:slug>/', views.app_detail, name='dashboard_app_detail'),
]
