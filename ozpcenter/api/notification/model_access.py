"""
Model access
"""
import datetime
import logging
import pytz

from django.db.models import Q
from django.db import transaction

from ozpcenter import errors

from ozpcenter.models import Notification
from ozpcenter.models import NotificationMailBox
from ozpcenter.models import Profile
from ozpcenter.models import Listing
from ozpcenter.models import ApplicationLibraryEntry

import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


permission_dict = {
    'APPS_MALL_STEWARD': [
        'add_system_notification',
        'change_system_notification',
        'delete_system_notification',

        'add_agency_notification',
        'change_agency_notification',
        'delete_agency_notification',

        'add_listing_notification',
        'change_listing_notification',
        'delete_listing_notification',

        'add_peer_notification',
        'change_peer_notification',
        'delete_peer_notification',

        'add_peer_bookmark_notification',
        'change_peer_bookmark_notification',
        'delete_peer_bookmark_notification',
    ],
    'ORG_STEWARD': [
        'add_system_notification',
        'change_system_notification',
        'delete_system_notification',

        'add_agency_notification',
        'change_agency_notification',
        'delete_agency_notification',

        'add_listing_notification',
        'change_listing_notification',
        'delete_listing_notification',

        'add_peer_notification',
        'change_peer_notification',
        'delete_peer_notification',

        'add_peer_bookmark_notification',
        'change_peer_bookmark_notification',
        'delete_peer_bookmark_notification',
    ],
    'USER': [
        'add_listing_notification',
        'change_listing_notification',
        'delete_listing_notification',

        'add_peer_notification',
        'change_peer_notification',
        'delete_peer_notification',

        'add_peer_bookmark_notification',
        'change_peer_bookmark_notification',
        'delete_peer_bookmark_notification',
        ]
}


def check_notification_permission(profile_instance, action, notification_type, **kwargs):
    """
    Check to see if user has permission
    """
    listing = kwargs.get('listing')
    notification = kwargs.get('notification')

    profile_role = profile_instance.highest_role()
    assert (profile_role in permission_dict), 'Profile group {} not found in permissions'.format(profile_role)

    user_action = '{}_{}_notification'.format(action, notification_type)

    profile_permission_list = permission_dict[profile_role]

    if user_action not in profile_permission_list:
        raise errors.PermissionDenied('Profile does not have [{}] permissions'.format(user_action))

    # If APP_MALL_STEWARD (Super User) Skip all sub check_notification_permission
    # TODO: Figure out if this correct (rivera)
    if profile_role == 'APPS_MALL_STEWARD' or profile_role == 'ORG_STEWARD':
        return True

    if notification_type == 'listing':
        if notification:
            listing = Listing.objects.get(id=notification.entity_id)

        if profile_instance not in listing.owners.all():
            raise errors.PermissionDenied('Cannot create a notification for a listing you do not own')
    return True


def get_self(username):
    """
    Get Profile for username

    Args:
        username (str): current username

    Returns:
        Profile if username exist, None if username does not exist
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
        django.db.models.query.QuerySet(Notification): List of all notifications
    """
    return Notification.objects.all()


def get_all_pending_notifications(for_user=False):
    """
    Gets all system-wide pending notifications
    V2

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
        django.db.models.query.QuerySet(Notification): List of system-wide pending notifications
    """
    unexpired_system_notifications = Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc))

    if for_user:
        unexpired_system_notifications = unexpired_system_notifications.filter(agency__isnull=True,
                                              listing__isnull=True,
                                              _peer__isnull=True)

    return unexpired_system_notifications


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
        django.db.models.query.QuerySet(Notification): List of system-wide pending notifications
    """
    expired_system_notifications = Notification.objects.filter(
        expires_date__lt=datetime.datetime.now(pytz.utc))
    return expired_system_notifications


def get_notification_by_id_mailbox(username, id, reraise=False):
    """
    Get Notification by id

    Args:
        id (int): id of notification
    """
    try:
        notifications_mailbox = NotificationMailBox.objects.filter(target_profile=get_self(username)).values_list('notification', flat=True)
        unexpired_notifications = Notification.objects.filter(pk__in=notifications_mailbox,
                                                    expires_date__gt=datetime.datetime.now(pytz.utc)).get(id=id)

        return unexpired_notifications
    except Notification.DoesNotExist as err:
        if reraise:
            raise err
        else:
            return None


def get_self_notifications_mailbox(username):
    """
    Get notifications for current user

    Args:
        username (str): current username to get notifications

    Returns:
        django.db.models.query.QuerySet(Notification): List of notifications for username
    """
    # TODO: Figure out how to do join query
    notifications_mailbox = NotificationMailBox.objects.filter(target_profile=get_self(username)).values_list('notification', flat=True)
    unexpired_notifications = Notification.objects.filter(pk__in=notifications_mailbox,
                                                expires_date__gt=datetime.datetime.now(pytz.utc))

    return unexpired_notifications


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
        PEER_BOOKMARK = 'peer_bookmark'  # Peer to Peer Bookmark Notifications
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
    group_target = group_target or Notification.ALL
    entities = entities or []
    query = None

    if notification_type == Notification.SYSTEM:
        query = Profile.objects

    elif notification_type == Notification.AGENCY or notification_type == Notification.AGENCY_BOOKMARK:
        query = Profile.objects.filter(Q(organizations__in=entities) | Q(stewarded_organizations__in=entities))

    elif notification_type == Notification.LISTING:
        # Assumes that entities is [models.Listings, ...]
        # TODO: Respect Private Apps
        if group_target == Notification.USER or group_target == Notification.ALL:
            # Get users that bookmarked that listing
            owner_id_list = ApplicationLibraryEntry.objects.filter(listing__in=entities,
                                                                   listing__isnull=False,
                                                                   listing__is_enabled=True,
                                                                   listing__is_deleted=False).values_list('owner', flat=True).distinct()
            query = Profile.objects.filter(id__in=owner_id_list)
        elif group_target == Notification.ORG_STEWARD:
            # get the ORG_STEWARD(s) for that listing's agency
            entities_agency = [entity.agency.id for entity in entities]
            query = Profile.objects.filter(stewarded_organizations__in=entities_agency).distinct()

        elif group_target == Notification.OWNER:
            # get the Owner(s) for that listing's agency
            entities_ids = [entity.id for entity in entities]
            listings_owners = Listing.objects.filter(id__in=entities_ids).values_list('owners').distinct()
            query = Profile.objects.filter(id__in=listings_owners).distinct()

    elif notification_type == Notification.PEER or notification_type == Notification.PEER_BOOKMARK:
        # Assumes that entities is [models.Profile, ...]
        entities_id = [entity.id for entity in entities]
        query = Profile.objects.filter(id__in=entities_id)

    else:
        raise Exception('Notification Type not valid')

    if group_target == Notification.ALL:
        pass  # No Filtering Needed
    elif group_target == Notification.STEWARDS:
        pass  # TODO
    elif group_target == Notification.USER:
        pass  # TODO

    return query.all()


# Method is decorated with @transaction.atomic to ensure all logic is executed in a single transaction
@transaction.atomic
def bulk_notifications_saver(notification_instances):
    # Loop over each store and invoke save() on each entry
    for notification_instance in notification_instances:
        notification_instance.save()


def create_notification(author_username=None,
                        expires_date=None,
                        message=None,
                        listing=None,
                        agency=None,
                        peer=None,
                        peer_profile=None,
                        group_target=Notification.ALL):
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
        Notification: Created Notification

    Raises:
        AssertionError: If author_username or expires_date or message is None
    """
    assert (author_username is not None), 'Author Username is necessary'
    assert (expires_date is not None), 'Expires Date is necessary'
    assert (message is not None), 'Message is necessary'
    assert not(
        listing is not None and agency is not None), 'Notications can not have listing and agency at the same time'

    notification_type = Notification.SYSTEM

    if listing is not None:
        notification_type = Notification.LISTING
    elif agency is not None:
        notification_type = Notification.AGENCY
    elif peer is not None:
        notification_type = Notification.PEER
        try:
            if peer and 'folder_name' in peer:
                notification_type = Notification.PEER_BOOKMARK
        except ValueError:
            # Ignore Value Errors
            pass

    user = generic_model_access.get_profile(author_username)
    # TODO: Check if user exist, if not throw Exception Error ?

    check_notification_permission(user, 'add', notification_type, listing=listing)

    notification = Notification(
        expires_date=expires_date,
        author=user,
        message=message,
        listing=listing,  # TODO (RIVERA): Remove
        agency=agency,  # TODO (RIVERA): Remove
        peer=peer)

    notification.notification_type = notification_type

    if notification_type == Notification.SYSTEM:
        notification.group_target = group_target
        notification.entity_id = None

    elif notification_type == Notification.AGENCY:
        notification.group_target = group_target
        notification.entity_id = agency.pk

    elif notification_type == Notification.AGENCY_BOOKMARK:
        notification.group_target = group_target
        notification.entity_id = agency.pk

    elif notification_type == Notification.LISTING:
        notification.group_target = group_target
        notification.entity_id = listing.pk

    elif notification_type == Notification.PEER:
        notification.group_target = 'user'
        notification.entity_id = peer_profile.id

    elif notification_type == Notification.PEER_BOOKMARK:
        notification.group_target = 'user'
        notification.entity_id = peer_profile.id

    notification.save()

    # Add NotificationMail
    entities = None
    if notification_type == Notification.LISTING:
        entities = [listing]
    elif notification_type == Notification.AGENCY or notification_type == Notification.AGENCY_BOOKMARK:
        entities = [agency]
    elif notification_type == Notification.PEER or notification_type == Notification.PEER_BOOKMARK:
        entities = [peer_profile]

    target_list = get_profile_target_list(notification_type, group_target=group_target, entities=entities)

    bulk_notification_list = []

    for target_profile in target_list:
        notificationv2 = NotificationMailBox()
        notificationv2.target_profile = target_profile
        notificationv2.notification = notification
        # All the flags default to false
        notificationv2.emailed_status = False

        bulk_notification_list.append(notificationv2)

        if len(bulk_notification_list) >= 2000:
            bulk_notifications_saver(bulk_notification_list)
            bulk_notification_list = []

    if bulk_notification_list:
        bulk_notifications_saver(bulk_notification_list)

    return notification


def update_notification(author_username, notification_instance, expires_date):
    """
    Update Notification

    Args:
        notification_instance (Notification): notification_instance
        author_username (str): Username of author

    Return:
        Notification: Updated Notification
    """
    user = generic_model_access.get_profile(author_username)  # TODO: Check if user exist, if not throw Exception Error ?

    check_notification_permission(user, 'change', notification_instance.notification_type, notification=notification_instance)

    notification_instance.expires_date = expires_date
    notification_instance.save()
    return notification_instance


def dismiss_notification_mailbox(notification_instance, username):
    """
    Dismissed a Notification

    It delete the Mailbox Entry for user

    Args:
        notification_instance (Notification): notification_instance
        username (string)

    Return:
        bool: Notification Dismissed
    """
    profile_instance = get_self(username)
    NotificationMailBox.objects.filter(target_profile=profile_instance,
                                       notification=notification_instance).delete()
    return True
