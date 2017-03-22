# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.db import migrations


def notification_type(notification):
    """
    Dynamically figure out Notification Type

    Types:
        SYSTEM - System-wide Notifications
        AGENCY - Agency-wide Notifications
        AGENCY.BOOKMARK - Agency-wide Bookmark Notifications # Not requirement (erivera 20160621)
        LISTING - Listing Notifications
        PEER - Peer to Peer Notifications
        PEER.BOOKMARK - Peer to Peer Bookmark Notifications
    """
    type_list = []
    peer_list = []

    if notification._peer:
        peer_list.append('PEER')

        try:
            json_obj = (json.loads(notification._peer))
            if json_obj and 'folder_name' in json_obj:
                peer_list.append('BOOKMARK')
        except ValueError:
            # Ignore Value Errors
            pass

    if peer_list:
        type_list.append('.'.join(peer_list))

    if notification.listing:
        type_list.append('LISTING')

    if notification.agency:
        type_list.append('AGENCY')

    if not type_list:
        type_list.append('SYSTEM')

    return ','.join(type_list)


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    print('Starting Process')

    Notification = apps.get_model('ozpcenter', 'Notification')

    for current_notification in Notification.objects.all():
        print('current_notification_pk: {}'.format(current_notification.pk))
        current_notification_notification_type = notification_type(current_notification)

        if current_notification_notification_type == 'SYSTEM':
            current_notification.notification_type = 'system'
            current_notification.group_target = 'all'
            current_notification.entity_id = None

        elif current_notification_notification_type == 'AGENCY':
            current_notification.notification_type = 'agency'
            current_notification.group_target = 'all'
            current_notification.entity_id = current_notification.agency.pk

        elif current_notification_notification_type == 'AGENCY.BOOKMARK':
            current_notification.notification_type = 'agency_bookmark'
            current_notification.group_target = 'all'
            current_notification.entity_id = current_notification.agency.pk

        elif current_notification_notification_type == 'LISTING':
            current_notification.notification_type = 'listing'
            current_notification.group_target = 'all'
            current_notification.entity_id = current_notification.listing.pk

        elif current_notification_notification_type == 'PEER':
            current_notification.notification_type = 'peer'
            current_notification.group_target = 'user'
            current_notification.entity_id = None

        elif current_notification_notification_type == 'PEER.BOOKMARK':
            current_notification.notification_type = 'peer_bookmark'
            current_notification.group_target = 'user'
            current_notification.entity_id = None

        current_notification.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0012_auto_20170322_1309'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
    ]
