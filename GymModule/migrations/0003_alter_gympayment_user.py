# Generated by Django 5.1.6 on 2025-02-22 14:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GymModule', '0002_gymuser_gymuserpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gympayment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
