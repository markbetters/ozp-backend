# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from ozpcenter.scripts import notification_migrate


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    # Migration code goes here
    notification_migrate.run()


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0012_notificationv2'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
    ]
