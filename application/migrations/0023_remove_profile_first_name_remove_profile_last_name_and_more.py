# Generated by Django 5.1.3 on 2024-11-29 03:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0022_profile_first_name_profile_last_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="First_name",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="Last_name",
        ),
        migrations.AddField(
            model_name="profile",
            name="firstname",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="lastname",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
