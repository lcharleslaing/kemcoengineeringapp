import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group


def user_profile_image_path(instance, filename):
    """Generate unique filename for profile images - ALWAYS unique"""
    # Get file extension
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    # Generate unique filename using user ID, timestamp, and UUID
    # This ensures EVERY upload gets a completely unique filename
    user_id = instance.user.id if instance.user and instance.user.id else 'temp'
    import time
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{user_id}_{timestamp}_{unique_id}.{ext}"
    return os.path.join('profile_images', filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(upload_to=user_profile_image_path, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        # Delete old image file when a new one is uploaded
        old_image_name = None
        if self.pk:
            try:
                old_instance = UserProfile.objects.get(pk=self.pk)
                if old_instance.profile_image and old_instance.profile_image.name:
                    old_image_name = old_instance.profile_image.name
            except Exception:
                pass
        
        # Save the instance (this saves the new image file)
        super().save(*args, **kwargs)
        
        # Delete old file after saving
        if old_image_name and self.profile_image and self.profile_image.name and old_image_name != self.profile_image.name:
            try:
                from django.core.files.storage import default_storage
                if default_storage.exists(old_image_name):
                    default_storage.delete(old_image_name)
            except Exception:
                pass
    
    @property
    def get_avatar_url(self):
        """Get avatar URL - simple, no fancy cache-busting."""
        if self.profile_image and self.profile_image.name:
            return self.profile_image.url
        return "https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class DashboardAppQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def visible_on_dashboard(self):
        return self.active().filter(show_in_dashboard=True)

    def for_user(self, user):
        if not user.is_authenticated:
            return self.none()

        qs = self.visible_on_dashboard()
        if user.is_superuser:
            return qs.distinct()

        user_group_ids = user.groups.values_list("id", flat=True)
        unrestricted = Q(allowed_groups__isnull=True)
        allowed = Q(allowed_groups__in=user_group_ids)
        return qs.filter(unrestricted | allowed).distinct()


class DashboardApp(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide the app everywhere without deleting it.",
    )
    show_in_dashboard = models.BooleanField(
        default=True,
        help_text="Controls if this appears as a card on the dashboard.",
    )
    allowed_groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="dashboard_apps",
        help_text="Leave empty to make the app available to all authenticated users.",
    )
    hero_image = models.URLField(
        blank=True,
        help_text="Optional image URL for the app detail page hero section.",
    )
    coming_soon_message = models.TextField(
        blank=True,
        help_text="Optional longer message for the coming soon page.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DashboardAppQuerySet.as_manager()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def visible_to_user(self, user):
        if not self.is_active:
            return False
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if self.allowed_groups.exists():
            return self.allowed_groups.filter(
                id__in=user.groups.values_list("id", flat=True)
            ).exists()
        return True
