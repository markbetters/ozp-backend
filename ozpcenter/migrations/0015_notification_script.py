# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from ozpcenter.scripts import notification_mailbox


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    # Migration code goes here
    notification_mailbox.run()


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0014_notificationmailbox'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
    ]
