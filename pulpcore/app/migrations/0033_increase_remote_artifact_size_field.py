# Generated by Django 2.2.12 on 2020-06-09 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_export_to_chunks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remoteartifact',
            name='size',
            field=models.BigIntegerField(null=True),
        ),
    ]
