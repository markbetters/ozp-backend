# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import uuid
import pytz
import datetime
import json


def get_self_notifications(apps, username):
    Notification = apps.get_model('ozpcenter', 'Notification')
    ApplicationLibraryEntry = apps.get_model('ozpcenter', 'ApplicationLibraryEntry')
    Profile = apps.get_model('ozpcenter', 'Profile')

    # Get all notifications that have been dismissed by this user
    dismissed_notifications = Notification.objects.filter(dismissed_by__user__username=username)

    # Get all unexpired notifications for listings in this user's library
    bookmarked_listing_ids = ApplicationLibraryEntry.objects \
        .filter(owner__user__username=username,
                listing__isnull=False,
                listing__is_enabled=True,
                listing__is_deleted=False) \
        .values_list('listing', flat=True)

    unexpired_listing_notifications = Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc),
        listing__pk_in=bookmarked_listing_ids,
        agency__isnull=True,  # Ensure there are no agency notifications
        _peer__isnull=True,  # Ensure there are no peer notifications
        listing__isnull=False)

    # Gets all notifications that are regarding a listing in this user's
    # agencies
    user_agency = Profile.objects.get(user__username=username).organizations.all()
    unexpired_agency_notifications = Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc),
        agency__pk_in=user_agency,
        listing__isnull=True)

    # Get all unexpired peer notification
    unexpired_peer_notifications = Notification.objects \
        .filter(_peer__isnull=False,
                agency__isnull=True,  # Ensure there are no agency notifications
                listing__isnull=True,  # Ensure there are no listing notifications
                expires_date__gt=datetime.datetime.now(pytz.utc),
                _peer__contains='"user": {"username": "%s"}' % (username))

    # Get all unexpired system-wide notifications
    unexpired_system_notifications = Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc)).filter(agency__isnull=True,
                                              listing__isnull=True,
                                              _peer__isnull=True)

    # return (unexpired_system_notifications +
    # unexpired_listing_notifications) - dismissed_notifications
    notifications = (unexpired_system_notifications | unexpired_agency_notifications | unexpired_peer_notifications |
                     unexpired_listing_notifications).exclude(pk__in=dismissed_notifications)

    return notifications


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    # Migration code goes here
    print('starting Notification to NotificationV2 Migration')
    Profile = apps.get_model('ozpcenter', 'Profile')
    NotificationV2 = apps.get_model('ozpcenter', 'NotificationV2')

    for current_profile in Profile.objects.all():
        current_profile_username = current_profile.user.username
        current_notifications = get_self_notifications(apps, current_profile_username)
        current_notifications_len = len(current_notifications)
        print('==== Migrating {} notifications for user {} ==='.format(current_notifications_len, current_profile_username))

        for current_notification in current_notifications:
            current_notification_created_date = current_notification.created_date
            current_notification_expires_date = current_notification.expires_date
            current_notification_author = current_notification.author
            current_notification_message = current_notification.message

            # notifications type
            type_list = []
            peer_list = []

            if current_notification._peer:
                peer_list.append('PEER')

                try:
                    json_obj = (current_notification._peer)
                    if json_obj and 'folder_name' in json_obj:
                        peer_list.append('BOOKMARK')
                except ValueError:
                    # Ignore Value Errors
                    pass

            if peer_list:
                type_list.append('.'.join(peer_list))

            if current_notification.listing:
                type_list.append('LISTING')

            if current_notification.agency:
                type_list.append('AGENCY')

            if not type_list:
                type_list.append('SYSTEM')

            current_notification_notification_type = ','.join(type_list)
            current_notification_listing = current_notification.listing
            current_notification_agency = current_notification.agency

            current_notification_peer = None
            if current_notification._peer:
                current_notification_peer = json.loads(current_notification._peer)
            else:
                current_notification_peer = None

            # NotificationV2
            notification_id = uuid.uuid5(uuid.NAMESPACE_DNS, str(current_notification.pk))
            notificationv2 = NotificationV2()
            notificationv2.profile_target_id = current_profile

            notificationv2.created_date = current_notification_created_date
            notificationv2.expires_date = current_notification_expires_date
            notificationv2.author = current_notification_author
            notificationv2.message = current_notification_message

            notificationv2.notification_id = notification_id

            if current_notification_notification_type == 'SYSTEM':
                notificationv2.notification_type = 'system'
                notificationv2.user_target = 'all'
                notificationv2.entity_id = None

            elif current_notification_notification_type == 'AGENCY':
                notificationv2.notification_type = 'agency'
                notificationv2.user_target = 'all'
                notificationv2.entity_id = current_notification_agency.pk

            elif current_notification_notification_type == 'AGENCY.BOOKMARK':
                notificationv2.notification_type = 'agency_bookmark'
                notificationv2.user_target = 'all'
                notificationv2.entity_id = current_notification_agency.pk
                notificationv2.metadata = current_notification_peer

            elif current_notification_notification_type == 'LISTING':
                notificationv2.notification_type = 'listing'
                notificationv2.user_target = 'all'
                notificationv2.entity_id = current_notification_listing.pk

            elif current_notification_notification_type == 'PEER':
                notificationv2.notification_type = 'peer'
                notificationv2.user_target = 'user'
                notificationv2.entity_id = None

            elif current_notification_notification_type == 'PEER.BOOKMARK':
                notificationv2.notification_type = 'peer_bookmark'
                notificationv2.user_target = 'user'
                notificationv2.entity_id = None
                notificationv2.metadata = current_notification_peer

            notificationv2.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0012_notificationv2'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
    ]
