# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-10 23:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blurber', '0004_auto_20160227_1327'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-create_date'], 'permissions': (('can_edit_blurb', 'Editor can edit blurb'),)},
        ),
        migrations.AlterModelOptions(
            name='song',
            options={'ordering': ['-upload_date'], 'permissions': (('can_edit_overall_score', 'Editor can edit overall score'),)},
        ),
    ]
