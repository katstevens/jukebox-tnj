# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-12-28 17:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tsj', '0003_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='published_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]
