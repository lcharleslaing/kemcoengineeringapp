from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import SiteSettingsForm
from .models import SiteSettings


@login_required
def site_settings_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied

    settings_obj = SiteSettings.get_solo()
    if request.method == "POST":
        form = SiteSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings updated.")
            return redirect("site_settings:site_settings")
    else:
        form = SiteSettingsForm(instance=settings_obj)

    return render(
        request,
        "site_settings/site_settings.html",
        {
            "form": form,
            "settings_obj": settings_obj,
        },
    )
