from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import SiteSettings


class SiteSettingsTests(TestCase):
    def test_get_solo_creates_singleton(self):
        first = SiteSettings.get_solo()
        second = SiteSettings.get_solo()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_registration_toggle(self):
        settings_obj = SiteSettings.get_solo()
        self.assertFalse(settings_obj.registration_requires_invite)
        settings_obj.registration_requires_invite = True
        settings_obj.save()
        refreshed = SiteSettings.get_solo()
        self.assertTrue(refreshed.registration_requires_invite)


class SiteSettingsViewTests(TestCase):
    def setUp(self):
        self.settings_url = reverse("site_settings:site_settings")
        self.staff_user = User.objects.create_user(
            username="staff", password="password", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="regular", password="password"
        )

    def test_staff_can_view_settings_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Site Settings")

    def test_non_staff_blocked_from_settings_page(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 403)
