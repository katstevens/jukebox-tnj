# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-01 14:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writers', '0006_data_add_editor_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='writer',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]
