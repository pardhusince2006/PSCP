# Generated by Django 5.2 on 2025-04-04 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0006_project_is_submitted"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
    ]
