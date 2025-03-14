# Generated by Django 5.1.6 on 2025-03-05 16:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GymModule', '0015_remove_user_biometric_type_gymuser_biometric_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_time', models.TimeField(auto_now_add=True)),
                ('login_date', models.DateField(auto_now_add=True)),
                ('logout_time', models.TimeField(auto_now_add=True)),
                ('gym_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GymModule.gymuser')),
            ],
        ),
    ]
