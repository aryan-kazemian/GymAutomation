# Generated by Django 5.2.1 on 2025-05-10 11:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LogModule', '0002_initial'),
        ('UserModule', '0003_genmembershiptype_genshift_secaccess_genperson_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserModule.genmember'),
        ),
    ]
