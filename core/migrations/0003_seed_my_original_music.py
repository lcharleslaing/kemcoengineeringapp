from django.db import migrations


def seed_my_original_music(apps, schema_editor):
    DashboardApp = apps.get_model("core", "DashboardApp")
    DashboardApp.objects.update_or_create(
        slug="my-original-music",
        defaults={
            "title": "My Original Music",
            "short_description": "Original tracks, demos, and stories from the studio.",
            "coming_soon_message": (
                "We're tuning up a dedicated home for every beat, lyric, and melody. "
                "From early sketches to full studio productions, you'll get an inside look "
                "at how each song comes to life."
            ),
        },
    )


def unseed_my_original_music(apps, schema_editor):
    DashboardApp = apps.get_model("core", "DashboardApp")
    DashboardApp.objects.filter(slug="my-original-music").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_dashboardapp"),
    ]

    operations = [
        migrations.RunPython(seed_my_original_music, unseed_my_original_music),
    ]
