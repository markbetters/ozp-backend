"""
Migrating Old Notification Model to NotificationV2 Model for development
This is for "make dev"

For existing databases, 0013_notification_script will run

"""
from PIL import Image
import datetime
import json
import os
import pytz
import sys
import uuid

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from django.contrib import auth
from django.conf import settings

from ozpcenter import model_access
from ozpcenter import models
import ozpcenter.api.listing.model_access as listing_model_access


TEST_IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images') + '/'

DEMO_APP_ROOT = settings.OZP['DEMO_APP_ROOT']


def get_self_notifications(username):
    # Get all notifications that have been dismissed by this user
    dismissed_notifications = models.Notification.objects.filter(dismissed_by__user__username=username)

    # Get all unexpired notifications for listings in this user's library
    bookmarked_listing_ids = models.ApplicationLibraryEntry.objects \
        .filter(owner__user__username=username,
                listing__isnull=False,
                listing__is_enabled=True,
                listing__is_deleted=False) \
        .values_list('listing', flat=True)

    unexpired_listing_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc),
        listing__pk_in=bookmarked_listing_ids,
        agency__isnull=True,  # Ensure there are no agency notifications
        _peer__isnull=True,  # Ensure there are no peer notifications
        listing__isnull=False)

    # Gets all notifications that are regarding a listing in this user's
    # agencies
    user_agency = models.Profile.objects.get(user__username=username).organizations.all()
    unexpired_agency_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc),
        agency__pk_in=user_agency,
        listing__isnull=True)

    # Get all unexpired peer notification
    unexpired_peer_notifications = models.Notification.objects \
        .filter(_peer__isnull=False,
                agency__isnull=True,  # Ensure there are no agency notifications
                listing__isnull=True,  # Ensure there are no listing notifications
                expires_date__gt=datetime.datetime.now(pytz.utc),
                _peer__contains='"user": {"username": "%s"}' % (username))

    # Get all unexpired system-wide notifications
    unexpired_system_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc)).filter(agency__isnull=True,
                                              listing__isnull=True,
                                              _peer__isnull=True)

    # return (unexpired_system_notifications +
    # unexpired_listing_notifications) - dismissed_notifications
    notifications = (unexpired_system_notifications | unexpired_agency_notifications | unexpired_peer_notifications |
                     unexpired_listing_notifications).exclude(pk__in=dismissed_notifications)

    return notifications


def run():
    """
    Creates basic sample data
    """
    if models.NotificationV2.objects.count() == 0:
        # Migration code goes here
        print('starting Notification to NotificationV2 Migration')

        for current_profile in models.Profile.objects.all():
            current_profile_username = current_profile.user.username
            current_notifications = get_self_notifications(current_profile_username)
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

                notificationv2 = models.NotificationV2()
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
