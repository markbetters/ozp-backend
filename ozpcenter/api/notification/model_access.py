"""
Model access
"""
import datetime
import logging
import pytz

from ozpcenter import models
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def create_notification(expires_date, author_username, message, listing=None):
    """
    Create Notification

    Args:
        expires_date (datetime.datetime): Expires Date (datetime.datetime(2016, 6, 24, 1, 0, tzinfo=<UTC>))
        author_username (str): Username of author
        message (str): Message of notification
        listing (models.Listing-Optional): Listing
    Return:
        models.Notification: Created Notification
    """
    user = generic_model_access.get_profile(author_username)
    # TODO: Check if user exist, if not throw Exception Error ?

    notification = models.Notification(
        expires_date=expires_date,
        author=user,
        message=message,
        listing=listing)

    notification.save()
    return notification


def dismiss_notification(notification_instance, username):
    """
    Create Notification

    Args:
        notification_instance (models.Notification): notification_instance)
        username (string)
    Return:
        bool: Notification Dismissed
    """
    user = generic_model_access.get_profile(username)
    notification_instance.dismissed_by.add(user)

    return True


def update_notification(notification_instance, expires_date):
    """
    Update Notification

    Args:
        notification_instance (models.Notification): notification_instance
        author_username (str): Username of author
    Return:
        models.Notification: Updated Notification
    """
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


def get_self_notifications(username):
    """
    Get notifications for current user

    get all notifications that have not yet expired AND:
        * have not been dismissed by this user
        * are regarding a listing in this user's library (if the
            notification is listing-specific)

    Args:
        username (str): current username to get notifications

    Returns:
        [models.Notification]: List of notification for username
        else [] if no notifications exists for username
    """
    # Get all notifications that have been dismissed by this user
    dismissed_notifications = models.Notification.objects.filter(
        dismissed_by__user__username=username)

    # Get all unexpired notifications for listings in this user's library
    bookmarked_listing_ids = models.ApplicationLibraryEntry.objects \
        .filter(owner__user__username=username) \
        .filter(listing__is_enabled=True) \
        .filter(listing__is_deleted=False) \
        .values_list('listing', flat=True)

    unexpired_listing_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc), listing__pk_in=bookmarked_listing_ids)

    # Get all unexpired system-wide notifications
    unexpired_system_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc), listing__isnull=True)

    # return (unexpired_system_notifications + unexpired_listing_notifications) -
    #    dismissed_notifications
    notifications = (unexpired_system_notifications | unexpired_listing_notifications).exclude(
        pk__in=dismissed_notifications)

    return notifications


def get_all_pending_notifications():
    """
    Gets all system-wide pending notifications

    Returns:
        [models.Notification]: List of system-wide pending notifications
        else [] if no notifications exists
    """
    unexpired_system_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc))
    return unexpired_system_notifications


def get_all_expired_notifications():
    """
    Get All Expired Notifications

    Returns:
        [models.Notification]: List of system-wide pending notifications
        else [] if no notifications exists
    """
    expired_system_notifications = models.Notification.objects.filter(
        expires_date__lt=datetime.datetime.now(pytz.utc))
    return expired_system_notifications


def get_all_notifications():
    """
    Get All System-Wide Notifications

    Returns:
        [models.Notification]: List of System-Wide Notifications
        else [] if no notifications exists
    """
    return models.Notification.objects.all()
