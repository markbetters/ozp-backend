"""
Model access
"""
import datetime
import json
import logging
import pytz
from enum import Enum

from ozpcenter import errors
from ozpcenter import models
import ozpcenter.model_access as generic_model_access


# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class UserRoleType(Enum):
    APPS_MALL_STEWARD = 'APPS_MALL_STEWARD'
    ORG_STEWARD = 'ORG_STEWARD'
    USER = 'USER'


class NotificationActionEnum(Enum):
    CREATE = 'Create'
    UPDATE = 'Update'
    DELETE = 'Delete'


class NotificationTypeEnum(Enum):
    SYSTEM = 'system'
    AGENCY = 'agency'
    AGENCY_BOOKMARK = 'agency_bookmark'
    LISTING = 'lising'
    PEER = 'peer'
    PEER_BOOKMARK = 'peer_bookmark'


def org_create_listing_condition(profile_obj, listing):
    """
    """
    if profile_obj not in listing.owners.all():
        raise errors.PermissionDenied(
            'Cannot create a notification for a listing you do not own')
    return True


def user_create_listing_condition(profile_obj, listing):
    """
    Listing create condition for user

    Args:
        profile_obj (models.Profile): Profile
        listing (models.Listing): Listing

    Return:
        bool: if user can create listings
    """
    if profile_obj not in listing.owners.all():
        raise errors.PermissionDenied(
            'Cannot create a notification for a listing you do not own')
    return True


def raise_(exception):
    """
    Helper Function to raise exceptions

    Arg:
        exception (Exception): Exception class
    """
    raise exception


def _check_profile_permission(user_role_type, notification_action, notification_type, **kwargs):
    """
    Check Permission

    Permissions:
        APP_MALL_STEWARD
            can [CREATE, UPDATE, DISMISS, DELETE]
            notification type [SYSTEM, AGENCY, LISTING]

        ORG_STEWARD
            can [CREATE, UPDATE, DISMISS]
            notification type [AGENCY(org_steward_agency_condition), LISTING(c2)]
        USER
            can [CREATE, DISMISS]
            notification type [LISTING(c3)]

    Return:
        lambda function
    """
    profile_obj = kwargs.get('profile_obj')
    listing = kwargs.get('listing')

    permissions = {
        UserRoleType.APPS_MALL_STEWARD: {
            NotificationActionEnum.CREATE: {
                NotificationTypeEnum.SYSTEM: lambda: True,
                NotificationTypeEnum.AGENCY: lambda: True,
                NotificationTypeEnum.LISTING: lambda: True,
                NotificationTypeEnum.PEER: lambda: True
            },
            NotificationActionEnum.UPDATE: {
                NotificationTypeEnum.SYSTEM: lambda: True,
                NotificationTypeEnum.AGENCY: lambda: True,
                NotificationTypeEnum.LISTING: lambda: True,
                NotificationTypeEnum.PEER: lambda: True
            },
            NotificationActionEnum.DELETE: {
                NotificationTypeEnum.SYSTEM: lambda: True,
                NotificationTypeEnum.AGENCY: lambda: True,
                NotificationTypeEnum.LISTING: lambda: True,
                NotificationTypeEnum.PEER: lambda: True
            }
        },
        UserRoleType.ORG_STEWARD: {
            NotificationActionEnum.CREATE: {
                NotificationTypeEnum.SYSTEM: lambda: raise_(errors.PermissionDenied('Only app mall stewards can create system notifications')),
                NotificationTypeEnum.AGENCY: lambda: True,
                NotificationTypeEnum.LISTING: lambda: True,  # TODO: org_create_listing_condition(profile_obj, listing)
                NotificationTypeEnum.PEER: lambda: True
            },
            NotificationActionEnum.UPDATE: {
                # lambda: raise_(errors.PermissionDenied('Only app mall
                # stewards can update system notifications')),
                NotificationTypeEnum.SYSTEM: lambda: True,
                NotificationTypeEnum.AGENCY: lambda: True,
                NotificationTypeEnum.LISTING: lambda: True,
                NotificationTypeEnum.PEER: lambda: True
            },
            NotificationActionEnum.DELETE: {
                # lambda: raise_(errors.PermissionDenied('Only app mall
                # stewards can delete system notifications')),
                NotificationTypeEnum.SYSTEM: lambda: True,
                NotificationTypeEnum.AGENCY: lambda: True,
                NotificationTypeEnum.LISTING: lambda: True,
                NotificationTypeEnum.PEER: lambda: True
            }
        },
        UserRoleType.USER: {
            NotificationActionEnum.CREATE: {
                NotificationTypeEnum.SYSTEM: lambda: raise_(errors.PermissionDenied('Only app mall stewards can create system notifications')),
                NotificationTypeEnum.AGENCY: lambda: raise_(errors.PermissionDenied('Only org stewards can create agency notifications')),
                NotificationTypeEnum.LISTING: lambda: user_create_listing_condition(profile_obj, listing),
                NotificationTypeEnum.PEER: lambda: True
            },
            NotificationActionEnum.UPDATE: {
                NotificationTypeEnum.SYSTEM: lambda: raise_(errors.PermissionDenied('Only app mall stewards can update system notifications')),
                NotificationTypeEnum.AGENCY: lambda: raise_(errors.PermissionDenied('Only org stewards can create agency notifications')),
                NotificationTypeEnum.LISTING: None,
                NotificationTypeEnum.PEER: lambda: True
            },
            NotificationActionEnum.DELETE: {
                NotificationTypeEnum.SYSTEM: lambda: raise_(errors.PermissionDenied('Only app mall stewards can delete system notifications')),
                NotificationTypeEnum.AGENCY: lambda: raise_(errors.PermissionDenied('Only org stewards can create agency notifications')),
                NotificationTypeEnum.LISTING: None,
                NotificationTypeEnum.PEER: lambda: True
            }
        }
    }
    return permissions.get(user_role_type, {}).get(notification_action, {}).get(notification_type, lambda: raise_(errors.PermissionDenied('Unknown Permissions')))


def get_profile_target_list(notification_type, group_target=None, entities=None):
    """
    This functions get a list of target profiles to send notifications to

    Notification Type
        SYSTEM = 'system'  # System-wide Notifications
            Get all users
        AGENCY = 'agency'  # Agency-wide Notifications
            Get all users from one or more agencies
        AGENCY_BOOKMARK = 'agency_bookmark'  # Agency-wide Bookmark Notifications # Not requirement (erivera 20160621)
            Get all users from one or more agencies and add Bookmark Folder id
        LISTING = 'listing'  # Listing Notifications
            Get all users that has Bookmark one or more listings
        PEER = 'peer'  # Peer to Peer Notifications
            Get list of users
        PEER_BOOKMARK = 'peer_bookmark'  # PEER.BOOKMARK - Peer to Peer Bookmark Notifications
            Get list of users

    Group Target
        ALL = 'all'  # All users
        STEWARDS = 'stewards'
        APP_STEWARD = 'app_steward'
        ORG_STEWARD = 'org_steward'
        USER = 'user'

    Args:
        notification_type: list of strings
        group_target: string
        entities: Model Objects of entities for the notification_type

    returns:
        [Profile, Profile, ...]
    """
    group_target = group_target or 'all'
    entities = entities or []
    query = None

    if notification_type == 'system':
        query = models.Profile.objects
    elif notification_type == 'agency':
        query = models.Profile.objects.filter(organizations__in=entities)
    elif notification_type == 'agency_bookmark':
        query = models.Profile.objects.filter(organizations__in=entities)
    elif notification_type == 'listing':
        # bookmarked_listing_ids = models.ApplicationLibraryEntry.objects \
        #     .filter(listing__in=entities,
        #             listing__isnull=False,
        #             listing__is_enabled=True,
        #             listing__is_deleted=False) \
        #     .values_list('owner', flat=True)

        query = models.Profile.objects.filter(organizations__in=entities)
    else:
        return []
    return query.all()


def get_notification_type(notification):
    """
    Dynamically figure out Notification Type

    Types:
        SYSTEM - System-wide Notifications
        AGENCY - Agency-wide Notifications
        AGENCY_BOOKMARK - Agency-wide Bookmark Notifications # Not requirement (erivera 20160621)
        LISTING - Listing Notifications
        PEER - Peer to Peer Notifications
        PEER_BOOKMARK - Peer to Peer Bookmark Notifications
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

    return '_'.join(type_list)


def create_notification(author_username, expires_date, message, listing=None, agency=None, peer=None):
    """
    Create Notification

    Notifications Types:
        * System-Wide Notification is made up of [expires_date, author_username, message]
        * Agency-Wide Notification is made up of [expires_date, author_username, message, agency]
        * Listing-Specific Notification is made up of [expires_date, author_username, message, listing]

    Args:
        author_username (str): Username of author
        expires_date (datetime.datetime): Expires Date (datetime.datetime(2016, 6, 24, 1, 0, tzinfo=<UTC>))
        message (str): Message of notification
        listing (models.Listing)-Optional: Listing
        Agency (models.Agency)-Optional: Agency

    Return:
        models.Notification: Created Notification

    Raises:
        AssertionError: If author_username or expires_date or message is None
    """
    assert (author_username is not None), 'Author Username is necessary'
    assert (expires_date is not None), 'Expires Date is necessary'
    assert (message is not None), 'Message is necessary'
    assert not(
        listing is not None and agency is not None), 'Notications can not have listing and agency at the same time'

    notification_action = NotificationActionEnum.CREATE
    notification_type = NotificationTypeEnum.SYSTEM

    if listing is not None:
        notification_type = NotificationTypeEnum.LISTING
    elif agency is not None:
        notification_type = NotificationTypeEnum.AGENCY
    elif peer is not None:
        notification_type = NotificationTypeEnum.PEER

    user = generic_model_access.get_profile(author_username)
    # TODO: Check if user exist, if not throw Exception Error ?

    user_role_type = UserRoleType(user.highest_role())

    _check_profile_permission(user_role_type,
                              notification_action,
                              notification_type,
                              listing=listing,
                              agency=agency)()

    notification = models.Notification(
        expires_date=expires_date,
        author=user,
        message=message,
        listing=listing,
        agency=agency,
        peer=peer)

    current_notification_type = get_notification_type(notification)

    if current_notification_type == 'SYSTEM':
        notification.notification_type = 'system'
        notification.group_target = 'all'
        notification.entity_id = None

    elif current_notification_type == 'AGENCY':
        notification.notification_type = 'agency'
        notification.group_target = 'all'
        notification.entity_id = notification.agency.pk

    elif current_notification_type == 'AGENCY.BOOKMARK':
        notification.notification_type = 'agency_bookmark'
        notification.group_target = 'all'
        notification.entity_id = notification.agency.pk

    elif current_notification_type == 'LISTING':
        notification.notification_type = 'listing'
        notification.group_target = 'all'
        notification.entity_id = notification.listing.pk

    elif current_notification_type == 'PEER':
        notification.notification_type = 'peer'
        notification.group_target = 'user'
        notification.entity_id = None

    elif current_notification_type == 'PEER.BOOKMARK':
        notification.notification_type = 'peer_bookmark'
        notification.group_target = 'user'
        notification.entity_id = None

    notification.save()

    # Add NotificationV2
    return notification


def dismiss_notification(notification_instance, username):
    """
    Dismissed a Notification

    Args:
        notification_instance (models.Notification): notification_instance
        username (string)

    Return:
        bool: Notification Dismissed
    """
    user = generic_model_access.get_profile(username)
    notification_instance.dismissed_by.add(user)

    return True


def update_notification(author_username, notification_instance, expires_date):
    """
    Update Notification

    Args:
        notification_instance (models.Notification): notification_instance
        author_username (str): Username of author

    Return:
        models.Notification: Updated Notification
    """
    notification_action = NotificationActionEnum.UPDATE

    notification_type = NotificationTypeEnum.SYSTEM

    if notification_instance.listing is not None:
        notification_type = NotificationTypeEnum.LISTING
    elif notification_instance.agency is not None:
        notification_type = NotificationTypeEnum.AGENCY

    user = generic_model_access.get_profile(author_username)
    # TODO: Check if user exist, if not throw Exception Error ?

    user_role_type = UserRoleType(user.highest_role())

    _check_profile_permission(
        user_role_type, notification_action, notification_type)()

    notification_instance.expires_date = expires_date
    notification_instance.save()
    return notification_instance


def get_self(username):
    """
    Get Profile for username

    Args:
        username (str): current username

    Returns:
        models.Profile if username exist, None if username does not exist
    """
    return generic_model_access.get_profile(username)


def get_all_notifications():
    """
    Get all notifications (expired and un-expired notifications)

    Includes
    * Listing Notifications
    * Agency Notifications
    * System Notifications
    * Peer Notifications
    * Peer.Bookmark Notifications

    Returns:
        django.db.models.query.QuerySet(models.Notification): List of all notifications
    """
    return models.Notification.objects.all()

#
# def get_all_notifications_v2():
#     """
#     Get all notifications (expired and un-expired notifications)
#
#     Includes
#     * Listing Notifications
#     * Agency Notifications
#     * System Notifications
#     * Peer Notifications
#     * Peer.Bookmark Notifications
#
#     Returns:
#         django.db.models.query.QuerySet(models.Notification): List of all notifications
#     """
#     query = models.NotificationV2.objects.all()
#     # values('notification_id',
#     #         'created_date',
#     #         'expires_date',
#     #         'author_username',
#     #         'message',
#     #         'notification_type',
#     #         '_metadata').distinct()
#     return query


def get_all_pending_notifications(for_user=False):
    """
    Gets all system-wide pending notifications

    if for_user:
        Includes
         * System Notifications
    else:
        Includes
         * System Notifications
         * Listing Notifications
         * Agency Notifications
         * Peer Notifications
         * Peer.Bookmark Notifications

    Returns:
        django.db.models.query.QuerySet(models.Notification): List of system-wide pending notifications
    """
    unexpired_system_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc))

    if for_user:
        unexpired_system_notifications = unexpired_system_notifications.filter(agency__isnull=True,
                                              listing__isnull=True,
                                              _peer__isnull=True)

    return unexpired_system_notifications


def get_pending_peer_notifications(username):
    """
    Gets all pending peer notifications

    Includes
     * Peer Notifications
     * Peer.Bookmark Notifications

    Excludes
     * System Notifications
     * Listing Notifications
     * Agency Notifications

    Returns:
        django.db.models.query.QuerySet(models.Notification): List of system-wide pending notifications
    """
    unexpired_peer_notifications = models.Notification.objects \
        .filter(_peer__isnull=False,
                agency__isnull=True,  # Ensure there are no agency notifications
                listing__isnull=True,  # Ensure there are no listing notifications
                expires_date__gt=datetime.datetime.now(pytz.utc),
                _peer__contains='"user": {"username": "%s"}' % (username))

    return unexpired_peer_notifications


def get_listing_pending_notifications(username):
    """
    Gets all notifications that are regarding a listing in this user's library

    Includes
     * Listing Notifications

    Does not include
     * System Notifications
     * Agency Notifications
     * Peer Notifications
     * Peer.Bookmark Notifications

    Args:
        username (str): current username to get notifications

    Returns:
        django.db.models.query.QuerySet(models.Notification): List of user's listing pending notifications
    """
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

    return unexpired_listing_notifications


def get_agency_pending_notifications(username):
    """
    Gets all notifications that are regarding a listing in this user's agencies

    Includes
     * Agency Notifications

    Does not include
     * System Notifications
     * Listing Notifications


    Args:
        username (str): current username to get notifications

    Returns:
        django.db.models.query.QuerySet(models.Notification): List of user's agencies pending notifications
    """
    user_agency = generic_model_access.get_profile(
        username).organizations.all()

    unexpired_agency_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc),
        agency__pk_in=user_agency,
        listing__isnull=True)

    return unexpired_agency_notifications


def get_all_expired_notifications():
    """
    Get all expired notifications

    Includes
    * Listing Notifications
    * Agency Notifications
    * System Notifications
    * Peer Notifications
    * Peer.Bookmark Notifications

    Returns:
        django.db.models.query.QuerySet(models.Notification): List of system-wide pending notifications
    """
    expired_system_notifications = models.Notification.objects.filter(
        expires_date__lt=datetime.datetime.now(pytz.utc))
    return expired_system_notifications


def get_dismissed_notifications(username):
    """
    Get all dismissed notifications for a user

    Args:
        username (str): current username to get dismissed notifications

    Returns:
        django.db.models.query.QuerySet(models.Notification): List of dismissed notifications
    """
    return models.Notification.objects.filter(dismissed_by__user__username=username)


def get_notification_by_id(username, id, reraise=False):
    """
    Get Notification by id

    Args:
        id (int): id of notification
    """
    try:
        dismissed_notifications = get_dismissed_notifications(username)
        return models.Notification.objects.exclude(pk__in=dismissed_notifications).get(id=id)
    except models.Notification.DoesNotExist as err:
        if reraise:
            raise err
        else:
            return None


def get_self_notifications(username):
    """
    Get notifications for current user

    User's Notifications are
        * Notifications that have not yet expired (A)
        * Notifications have not been dismissed by this user (B)
        * Notifications that are regarding a listing in this user's library
          if the notification is listing-specific
        * Notification that are System-wide are included

    Args:
        username (str): current username to get notifications

    Returns:
        django.db.models.query.QuerySet(models.Notification): List of notifications for username
    """
    # Get all notifications that have been dismissed by this user
    dismissed_notifications = get_dismissed_notifications(username)

    # Get all unexpired notifications for listings in this user's library
    unexpired_listing_notifications = get_listing_pending_notifications(
        username)

    # Gets all notifications that are regarding a listing in this user's
    # agencies
    unexpired_agency_notifications = get_agency_pending_notifications(username)

    # Get all unexpired peer notification
    unexpired_peer_notifications = get_pending_peer_notifications(username)

    # Get all unexpired system-wide notifications
    unexpired_system_notifications = get_all_pending_notifications(for_user=True)

    # return (unexpired_system_notifications +
    # unexpired_listing_notifications) - dismissed_notifications
    notifications = (unexpired_system_notifications | unexpired_agency_notifications | unexpired_peer_notifications |
                     unexpired_listing_notifications).exclude(pk__in=dismissed_notifications)

    return notifications

#
# def get_self_notifications_v2(username):
#     """
#     Get notifications for current user
#
#     Args:
#         username (str): current username to get notifications
#
#     Returns:
#         django.db.models.query.QuerySet(models.Notification): List of notifications for username
#     """
#     notifications = models.NotificationV2.objects.filter(target_profile=get_self(username))
#
#     return notifications
