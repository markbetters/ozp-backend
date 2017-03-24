"""
Migrating Old Notification Model to Notification Model for development
This is for "make dev"

For existing databases, 0015_notification_script will run

"""
import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

import json
from django.core.exceptions import ObjectDoesNotExist
from ozpcenter import models


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


def run():
    """
    Creates basic sample data
    """
    print('Starting Notification Fill Migration')

    Notification = models.Notification
    Profile = models.Profile

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

        elif current_notification_notification_type == 'AGENCY.BOOKMARK':  # This should not be common
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

        elif current_notification_notification_type == 'PEER.BOOKMARK':
            current_notification.notification_type = 'peer_bookmark'
            current_notification.group_target = 'user'

        if current_notification_notification_type == 'PEER' or current_notification_notification_type == 'PEER.BOOKMARK':
            entity_id = None
            try:
                json_obj = json.loads(current_notification._peer)
                current_username = json_obj.get('user').get('username')

                if json_obj:
                    profile_obj = None
                    try:
                        profile_obj = Profile.objects.get(user__username=current_username)
                    except ObjectDoesNotExist:
                        pass

                    if profile_obj:
                        entity_id = profile_obj.id
            except ValueError:
                # Ignore Value Errors
                pass
            current_notification.entity_id = entity_id

        current_notification.save()
