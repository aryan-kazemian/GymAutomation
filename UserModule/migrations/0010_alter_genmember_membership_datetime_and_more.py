# Generated by Django 5.2.1 on 2025-05-10 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserModule', '0009_alter_genperson_has_insurance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genmember',
            name='membership_datetime',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='genmember',
            name='modification_datetime',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
