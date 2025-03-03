# Generated by Django 5.1.6 on 2025-02-22 14:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GymModule', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GymUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('nation_cod', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('join_date', models.DateTimeField(auto_now_add=True)),
                ('expiration_date', models.DateTimeField(blank=True, null=True)),
                ('biometric_type', models.CharField(choices=[('finger_print', 'finger print'), ('face_scan', 'face scan')], default='finger_print', max_length=40)),
                ('fingerprint', models.BinaryField(blank=True, null=True)),
                ('face_image', models.ImageField(blank=True, null=True, upload_to='faces/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('gym', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GymUserPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payed_amount', models.CharField(max_length=120)),
                ('payed_date', models.DateTimeField(auto_now_add=True)),
                ('subscription_duration', models.CharField(choices=[('1_months', '1 months'), ('2_months', '2 months'), ('3_months', '3 months'), ('6_months', '6 months'), ('9_months', '9 months'), ('1_year', '1 year'), ('2_year', '2 year')], default='1_months', max_length=20)),
                ('is_first_save', models.BooleanField(default=False, editable=False)),
                ('gym_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GymModule.gymuser')),
            ],
        ),
    ]
