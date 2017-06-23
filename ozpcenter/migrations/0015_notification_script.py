# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import migrations
# from ozpcenter.scripts import notification_mailbox

DEV_MODE = bool(os.getenv('DEV_MODE', False))


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    if DEV_MODE is True:
        return
    # Migration code goes here
    # notification_mailbox.run()
    # Running the script automatically was making any change in the profile raise in exception
    print('Please Run - python manage.py runscript notification_mailbox')
    print('If it is the first time say N, run the script, and next time say Y')
    print('For Development Machines: Always say Y')

    response = input('Have you run command: Y/N    ').lower()

    if response == 'y':
        return
    else:
        raise Exception('You need to run command first')


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0014_notificationmailbox'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
    ]
