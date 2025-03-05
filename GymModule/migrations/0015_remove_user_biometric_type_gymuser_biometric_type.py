# Generated by Django 5.1.6 on 2025-03-05 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GymModule', '0014_gymuser_face_binary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='biometric_type',
        ),
        migrations.AddField(
            model_name='gymuser',
            name='biometric_type',
            field=models.CharField(choices=[('finger_print', 'finger print'), ('face_scan', 'face scan')], max_length=40, null=True),
        ),
    ]
