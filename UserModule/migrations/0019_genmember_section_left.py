# Generated by Django 5.2.1 on 2025-06-10 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserModule', '0018_genmember_creation_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='genmember',
            name='section_left',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
