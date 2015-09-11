"""
Model access
"""
import datetime
import logging
import pytz

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_self_notifications(username):
    """
    Get notifications for current user

    get all notifications that have not yet expired AND:
        * have not been dismissed by this user
        * are regarding a listing in this user's library (if the
            notification is listing-specific)
    """
    # get all notifications that have been dismissed by this user
    dismissed_notifications = models.Notification.objects.filter(
        dismissed_by__user__username=username)

    # TODO get all unexpired notifications for listings in this user's library

    # get all unexpired system-wide notifications
    unexpired_system_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc), listing__isnull=True)

    # return all_unexpired_notifications - dismissed_notifications
    notifications = unexpired_system_notifications.exclude(
        pk__in=dismissed_notifications)

    return notifications

def get_all_pending_notifications():
    unexpired_system_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(pytz.utc), listing__isnull=True)
    return unexpired_system_notifications

def get_all_expired_notifications():
    expired_system_notifications = models.Notification.objects.filter(
        expires_date__lt=datetime.datetime.now(pytz.utc), listing__isnull=True)
    return expired_system_notifications

def get_all_notifications():
    return models.Notification.objects.all()