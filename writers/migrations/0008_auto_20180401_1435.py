# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-01 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writers', '0007_writer_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='writer',
            name='bio_link_name',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='writer',
            name='public',
            field=models.BooleanField(default=True, help_text='Tick to show bio link on We Love Us list'),
        ),
    ]