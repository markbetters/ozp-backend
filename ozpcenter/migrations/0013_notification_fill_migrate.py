# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations

from ozpcenter.scripts import notification_fill


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    notification_fill.run()


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0012_auto_20170322_1309'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
    ]
