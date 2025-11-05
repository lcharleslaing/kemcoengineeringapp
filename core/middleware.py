from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, resolve_url
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import urlencode


class AdminAccessMiddleware(MiddlewareMixin):
    """Block access to the Django admin for non admin users."""

    def process_request(self, request):
        if not request.path.startswith("/admin"):
            return None

        if not request.user.is_authenticated:
            login_url = resolve_url(settings.LOGIN_URL)
            query = urlencode({"next": request.get_full_path()})
            return redirect(f"{login_url}?{query}")

        if request.user.is_superuser or request.user.is_staff:
            return None

        return HttpResponseForbidden("You do not have permission to access the admin dashboard.")
