# Generated by Django 5.2.1 on 2025-07-31 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LockerModule', '0004_locker_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='locker',
            name='locker_place',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
