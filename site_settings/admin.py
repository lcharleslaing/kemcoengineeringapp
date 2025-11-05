from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("registration_requires_invite", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context=None):
        if SiteSettings.objects.exists():
            settings_obj = SiteSettings.get_solo()
            return HttpResponseRedirect(
                reverse("admin:site_settings_sitesettings_change", args=[settings_obj.pk])
            )
        return super().changelist_view(request, extra_context=extra_context)
