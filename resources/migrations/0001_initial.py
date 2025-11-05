# Generated manually for Resources app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide this department')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide this role')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide this person')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about this person')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(blank=True, help_text='Department this person belongs to', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='people', to='resources.department')),
                ('role', models.ForeignKey(blank=True, help_text='Role/position of this person', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='people', to='resources.role')),
                ('user', models.OneToOneField(blank=True, help_text='Link to Django user account (optional)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_profile', to='auth.user')),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'People',
                'ordering': ['last_name', 'first_name'],
            },
        ),
    ]
