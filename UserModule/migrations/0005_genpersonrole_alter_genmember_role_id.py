# Generated by Django 5.2.1 on 2025-05-10 13:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserModule', '0004_remove_acctraffic_member_remove_acctraffic_shift_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenPersonRole',
            fields=[
                ('role_id', models.IntegerField(primary_key=True, serialize=False)),
                ('role_desc', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='genmember',
            name='role_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='UserModule.genpersonrole'),
        ),
    ]
