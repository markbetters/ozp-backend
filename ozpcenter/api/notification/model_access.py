"""
Model access
"""
import datetime
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.utils as utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_self_notifications(username):
    """
    Get notifications for current user

    get all notifications that have not yet expired AND:
        * have not been dismissed by this user
        * are regarding a listing in this user's library (if the
            notification is listing-specific)

    Key: notifications:<username>
    """
    # get all notifications that have been dismissed by this user
    dismissed_notifications = models.Notification.objects.filter(
        dismissed_by__user__username=username)

    # get all unexpired notifications for listings in this user's library

    # get all unexpired system-wide notifications
    unexpired_system_notifications = models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now(), listing__isnull=True)

    # return all_unexpired_notifications - dismissed_notifications

    return  models.Notification.objects.filter(
        expires_date__gt=datetime.datetime.now())