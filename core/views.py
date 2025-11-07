import json
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from openai import OpenAI

from .forms import CustomUserCreationForm, UserProfileForm
from .models import DashboardApp, UserProfile
from site_settings.models import SiteSettings


DEFAULT_DASHBOARD_APPS = [
    {
        "slug": "my-calendar",
        "title": "My Calendar",
        "short_description": "Organize your schedule, events, and important dates all in one place.",
        "coming_soon_message": (
            "We're building a beautiful calendar interface to help you manage your time effectively. "
            "Track appointments, set reminders, and never miss an important date. "
            "From daily tasks to long-term planning, your calendar will keep you on track."
        ),
    },
]


def ensure_default_dashboard_apps():
    try:
        # Get list of slugs that should be active
        active_slugs = {app["slug"] for app in DEFAULT_DASHBOARD_APPS}
        
        # Update or create apps that are in DEFAULT_DASHBOARD_APPS
        for definition in DEFAULT_DASHBOARD_APPS:
            defaults = {
                key: value
                for key, value in definition.items()
                if key not in {"slug"}
            }
            defaults.setdefault("show_in_dashboard", True)
            defaults.setdefault("is_active", True)
            DashboardApp.objects.update_or_create(
                slug=definition["slug"],
                defaults=defaults,
            )
        
        # Deactivate apps that are no longer in DEFAULT_DASHBOARD_APPS
        # This hides them from the dashboard without deleting them
        DashboardApp.objects.exclude(slug__in=active_slugs).update(
            is_active=False,
            show_in_dashboard=False
        )
    except (ProgrammingError, OperationalError):
        # Database tables might not exist during migrations or setup.
        return

# Initialize OpenAI client
def get_openai_client():
    """Get configured OpenAI client"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    client = OpenAI(
        api_key=api_key,
        organization=os.getenv('OPENAI_ORGANIZATION'),  # Optional
        base_url=os.getenv('OPENAI_BASE_URL'),  # Optional for custom endpoints
    )
    return client

@csrf_exempt
@require_http_methods(["POST"])
def chat_with_ai(request):
    """
    Simple chat endpoint that talks to OpenAI
    POST /api/chat/
    Body: {"message": "Your message here"}
    """
    try:
        # Parse request
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get OpenAI client
        client = get_openai_client()
        
        # Make API call
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[
                {"role": "user", "content": user_message}
            ],
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', 1000)),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', 0.7))
        )
        
        # Extract response
        ai_message = response.choices[0].message.content
        
        return JsonResponse({
            'success': True,
            'message': ai_message,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        })
        
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'OpenAI API error: {str(e)}'}, status=500)


@login_required
def index(request):
    """Render the Tailwind/DaisyUI dashboard."""
    user_name = ""
    if request.user.is_authenticated:
        user_name = request.user.get_short_name() or request.user.username

    ensure_default_dashboard_apps()

    context = {
        "user_name": user_name,
        "stats": [
            {"label": "Active Sessions", "value": "12", "delta": "+3 vs last hour"},
            {"label": "Queued Jobs", "value": "5", "delta": "2 deploying"},
            {"label": "API Latency", "value": "182ms", "delta": "-12% this week"},
            {"label": "Test Coverage", "value": "68%", "delta": "Target: 75%"},
        ],
        "recent_events": [
            {
                "time": "3 mins ago",
                "description": "Electron package rebuilt for Linux",
                "status_label": "Success",
                "status_badge": "success",
            },
            {
                "time": "25 mins ago",
                "description": "Django migrations executed (core 0002_dashboard)",
                "status_label": "Applied",
                "status_badge": "info",
            },
            {
                "time": "1 hour ago",
                "description": "OpenAI API key rotated in environment",
                "status_label": "Warning",
                "status_badge": "warning",
            },
        ],
        "project_status": [
            {
                "badge": "success",
                "label": "Healthy",
                "title": "Backend Services",
                "detail": "Django dev server reachable at http://127.0.0.1:8001.",
            },
            {
                "badge": "info",
                "label": "Queued",
                "title": "Desktop Packaging",
                "detail": "Run `npm run build` to create fresh distributables.",
            },
            {
                "badge": "warning",
                "label": "Action",
                "title": "Testing Coverage",
                "detail": "Add core feature tests in `core/tests.py` before release.",
            },
        ],
        "quick_actions": [
            {
                "label": "Run Django Tests",
                "href": "https://docs.djangoproject.com/en/5.0/topics/testing/",
                "badge": "python manage.py test",
            },
            {
                "label": "Package Electron App",
                "href": "https://www.electron.build/",
                "badge": "npm run build",
            },
            {
                "label": "Open Django Admin",
                "href": "/admin/",
                "badge": "Requires superuser",
            },
        ],
        "apps": DashboardApp.objects.for_user(request.user),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def app_detail(request, slug):
    """Render the detail page for a dashboard app; currently used as a coming soon page."""
    ensure_default_dashboard_apps()
    app = get_object_or_404(DashboardApp, slug=slug, is_active=True)
    if not app.visible_to_user(request.user):
        raise PermissionDenied("You do not have access to this app yet.")
    
    # Redirect to actual app if it's implemented
    if slug == "my-calendar":
        return redirect("/calendar/")
    
    return render(request, "core/app_detail.html", {"app": app})


# Authentication Views
def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if SiteSettings.get_solo().registration_requires_invite:
        return render(
            request,
            "core/registration_closed.html",
            {
                "title": "Registration Closed",
                "message": "Registration is by invitation only right now. Please contact the site owner for access.",
            },
            status=403,
        )
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile_view(request):
    """Handle user profile view and editing"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    except Exception:
        # If there's any error, create a new profile
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                # Check if a new image file was uploaded
                has_new_image = 'profile_image' in request.FILES
                old_image_name = profile.profile_image.name if profile.profile_image else None
                
                profile = form.save()
                # Get fresh from database
                profile.refresh_from_db()
                messages.success(request, 'Your profile has been updated successfully!')
                import time
                return redirect(f'{reverse("profile")}?t={int(time.time() * 1000)}')
            except Exception as e:
                import traceback
                messages.error(request, f'Error saving profile: {str(e)}')
                print(f"Profile save error: {traceback.format_exc()}")
    else:
        form = UserProfileForm(instance=profile)
    
    # Get fresh profile from database - CRITICAL to get latest image
    try:
        profile = UserProfile.objects.get(pk=profile.pk)
        print(f"DEBUG: Profile image in view: {profile.profile_image.name if profile.profile_image else 'None'}")
    except Exception:
        pass
    
    return render(request, 'core/profile.html', {'form': form, 'profile': profile})
