# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-12-28 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsj', '0002_auto_20181228_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mail', models.CharField(max_length=100)),
                ('website', models.CharField(blank=True, max_length=100, null=True)),
                ('comment_text', models.TextField()),
            ],
        ),
    ]