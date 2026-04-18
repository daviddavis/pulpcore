# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0148_artifact_artifact_domain_size_index"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskschedule",
            name="task_kwargs",
            field=models.JSONField(default=dict),
        ),
    ]
