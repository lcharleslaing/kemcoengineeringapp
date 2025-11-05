from django.db import migrations


def seed_my_credit_history(apps, schema_editor):
    DashboardApp = apps.get_model("core", "DashboardApp")
    DashboardApp.objects.update_or_create(
        slug="my-credit-history",
        defaults={
            "title": "My Credit History",
            "short_description": "Monitor credit score trends, accounts, and key milestones over time.",
            "coming_soon_message": (
                "We're designing a dashboard to track credit score changes, payment history, and account health. "
                "You'll soon be able to stay proactive with reminders, insights, and a clear timeline of your credit journey."
            ),
        },
    )


def unseed_my_credit_history(apps, schema_editor):
    DashboardApp = apps.get_model("core", "DashboardApp")
    DashboardApp.objects.filter(slug="my-credit-history").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_seed_my_taxes"),
    ]

    operations = [
        migrations.RunPython(seed_my_credit_history, unseed_my_credit_history),
    ]
