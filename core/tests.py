from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from site_settings.models import SiteSettings

from .models import DashboardApp


class DashboardAppVisibilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="regular", password="password")
        self.client.force_login(self.user)
        DashboardApp.objects.all().delete()

    def test_app_visible_without_group_restrictions(self):
        app = DashboardApp.objects.create(
            title="Open Access App",
            slug="open-access-app",
            short_description="Available to everyone.",
        )

        self.assertTrue(app.visible_to_user(self.user))

    def test_app_hidden_when_user_missing_group(self):
        group = Group.objects.create(name="Creators")
        restricted_app = DashboardApp.objects.create(
            title="Restricted App",
            slug="restricted-app",
            short_description="Only for Creators.",
        )
        restricted_app.allowed_groups.add(group)

        self.assertFalse(restricted_app.visible_to_user(self.user))

        self.user.groups.add(group)
        self.assertTrue(restricted_app.visible_to_user(self.user))

    def test_dashboard_lists_only_visible_apps(self):
        public_app = DashboardApp.objects.create(
            title="Public App",
            slug="public-app",
            short_description="On display for everyone.",
        )
        hidden_app = DashboardApp.objects.create(
            title="Hidden App",
            slug="hidden-app",
            short_description="Should not show on dashboard.",
            show_in_dashboard=False,
        )
        group = Group.objects.create(name="Backstage")
        restricted_app = DashboardApp.objects.create(
            title="Restricted Dashboard App",
            slug="restricted-dashboard-app",
            short_description="Requires group access.",
        )
        restricted_app.allowed_groups.add(group)

        response = self.client.get(reverse("dashboard"))
        apps = list(response.context["apps"])
        self.assertIn(public_app, apps)
        self.assertNotIn(hidden_app, apps)
        self.assertNotIn(restricted_app, apps)

        self.user.groups.add(group)
        response = self.client.get(reverse("dashboard"))
        apps = list(response.context["apps"])
        self.assertIn(restricted_app, apps)

    def test_default_apps_seeded_on_dashboard_visit(self):
        DashboardApp.objects.all().delete()
        self.client.get(reverse("dashboard"))
        self.assertTrue(
            DashboardApp.objects.filter(slug="my-original-music").exists()
        )
        self.assertTrue(
            DashboardApp.objects.filter(slug="immigration-process").exists()
        )
        self.assertTrue(
            DashboardApp.objects.filter(slug="my-taxes").exists()
        )
        self.assertTrue(
            DashboardApp.objects.filter(slug="my-credit-history").exists()
        )

    def test_detail_view_respects_visibility(self):
        app = DashboardApp.objects.create(
            title="Detail App",
            slug="detail-app",
            short_description="Detail page ready.",
        )
        response = self.client.get(reverse("dashboard_app_detail", args=[app.slug]))
        self.assertEqual(response.status_code, 200)

        group = Group.objects.create(name="Hidden Group")
        hidden = DashboardApp.objects.create(
            title="Hidden Detail App",
            slug="hidden-detail-app",
            short_description="Should be blocked.",
        )
        hidden.allowed_groups.add(group)
        response = self.client.get(reverse("dashboard_app_detail", args=[hidden.slug]))
        self.assertEqual(response.status_code, 403)


class RegistrationViewTests(TestCase):
    def test_registration_open_by_default(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_registration_closed_when_invite_required(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.registration_requires_invite = True
        settings_obj.save()

        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "core/registration_closed.html")
