from django.db import migrations


def seed_my_taxes(apps, schema_editor):
    DashboardApp = apps.get_model("core", "DashboardApp")
    DashboardApp.objects.update_or_create(
        slug="my-taxes",
        defaults={
            "title": "My Taxes",
            "short_description": "Track income tax history, filings, and supporting documents in one place.",
            "coming_soon_message": (
                "We're building a secure space to organize yearly filings, deductions, and receipts. "
                "Soon you'll be able to see every tax season at a glance, stay ahead of deadlines, "
                "and keep your records tidy for peace of mind."
            ),
        },
    )


def unseed_my_taxes(apps, schema_editor):
    DashboardApp = apps.get_model("core", "DashboardApp")
    DashboardApp.objects.filter(slug="my-taxes").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_seed_immigration_process"),
    ]

    operations = [
        migrations.RunPython(seed_my_taxes, unseed_my_taxes),
    ]
