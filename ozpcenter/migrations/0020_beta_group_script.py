# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import Group


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    # Checks to see if beta_user group exists, if it does not create it
    group, created = Group.objects.get_or_create(name='BETA_USER')
    if created:
        print('BETA_USER Group Created')
    else:
        print('BETA_USER Group already exists')


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0019_auto_20170417_2045'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
    ]
