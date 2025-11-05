from django.db import models


class SiteSettings(models.Model):
    registration_requires_invite = models.BooleanField(
        default=False,
        help_text="When enabled, public user registration is disabled and invites are required.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        status = "Invite Only" if self.registration_requires_invite else "Open Registration"
        return f"Site Settings ({status})"

    @classmethod
    def get_solo(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance
