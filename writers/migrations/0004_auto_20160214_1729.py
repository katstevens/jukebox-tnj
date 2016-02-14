# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-14 17:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('writers', '0003_auto_20160214_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='writer',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='writer',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='writer',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='writer',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]