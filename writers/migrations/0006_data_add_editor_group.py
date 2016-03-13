# -*- coding: utf-8 -*-
# Manual migration
from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.auth.models import Permission, Group


def create_editor_group(apps, schema_editor):
    editor_group = Group.objects.get_or_create(name="tsj_editors")

    # Permissions created in blurber 0005
    can_change_blurb = Permission.objects.get(codename="can_edit_blurb")
    can_change_overall_score = Permission.objects.get(codename="can_edit_overall_score")
    editor_group.add(can_change_blurb)
    editor_group.add(can_change_overall_score)


def remove_editor_group(apps, schema_editor):
    Group = apps.get_model()

    try:
        editor_group = Group.objects.get(name="tsj_editors").delete()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ('writers', '0005_auto_20160227_1327'),
        ('blurber', '0005_auto_20160310_2302')
    ]

    operations = [
        migrations.RunPython(create_editor_group, remove_editor_group)
    ]
