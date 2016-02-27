# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-27 13:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blurber', '0003_song_mp3_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='sort_order',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='review',
            name='status',
            field=models.CharField(choices=[('', 'N/A'), ('draft', 'Draft'), ('saved', 'Saved'), ('published', 'Published'), ('removed', 'Removed')], default='draft', max_length=20),
        ),
        migrations.AlterField(
            model_name='scheduledweek',
            name='current_week',
            field=models.BooleanField(default=False, help_text='Show as the current scheduled week'),
        ),
        migrations.AlterField(
            model_name='song',
            name='status',
            field=models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('published', 'Published'), ('removed', 'Removed')], default='open', max_length=20),
        ),
    ]
