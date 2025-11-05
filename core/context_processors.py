def user_profile(request):
    """Add user profile to template context if user is authenticated"""
    context = {}
    if request.user.is_authenticated:
        try:
            # Get fresh profile from database to ensure we have latest image
            from core.models import UserProfile
            # ALWAYS get fresh from DB - never use cached
            profile = UserProfile.objects.select_related('user').get(user=request.user)
            context['user_profile'] = profile
        except UserProfile.DoesNotExist:
            context['user_profile'] = None
        except Exception:
            context['user_profile'] = None
    else:
        context['user_profile'] = None
    return context

