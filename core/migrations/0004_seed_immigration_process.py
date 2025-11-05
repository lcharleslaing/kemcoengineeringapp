from django.db import migrations


def seed_immigration_process(apps, schema_editor):
    DashboardApp = apps.get_model("core", "DashboardApp")
    DashboardApp.objects.update_or_create(
        slug="immigration-process",
        defaults={
            "title": "Immigration Process",
            "short_description": "Follow along as we document every milestone of bringing my wife home.",
            "coming_soon_message": (
                "We're mapping out each phase of the immigration journey - from paperwork prep "
                "to interview day. Expect clear timelines, checklists, and the personal notes that make "
                "this path easier to navigate together."
            ),
        },
    )


def unseed_immigration_process(apps, schema_editor):
    DashboardApp = apps.get_model("core", "DashboardApp")
    DashboardApp.objects.filter(slug="immigration-process").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_seed_my_original_music"),
    ]

    operations = [
        migrations.RunPython(seed_immigration_process, unseed_immigration_process),
    ]
