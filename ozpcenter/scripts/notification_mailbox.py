"""
Migrating Old Notification Model to NotificationV2 Model for development
This is for "make dev"

For existing databases, 0015_notification_script will run

"""
import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from ozpcenter import models


def get_self_notifications(username):
    """
    Getting all the notifications for a profile
    """
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
        # expires_date__gt=datetime.datetime.now(pytz.utc),
        listing__pk_in=bookmarked_listing_ids,
        agency__isnull=True,  # Ensure there are no agency notifications
        _peer__isnull=True,  # Ensure there are no peer notifications
        listing__isnull=False)

    # Gets all notifications that are regarding a listing in this user's
    # agencies
    user_agency = models.Profile.objects.get(user__username=username).organizations.all()
    unexpired_agency_notifications = models.Notification.objects.filter(
        # expires_date__gt=datetime.datetime.now(pytz.utc),
        agency__pk_in=user_agency,
        listing__isnull=True)

    # Get all unexpired peer notification
    unexpired_peer_notifications = models.Notification.objects \
        .filter(_peer__isnull=False,
                agency__isnull=True,  # Ensure there are no agency notifications
                listing__isnull=True,  # Ensure there are no listing notifications
                # expires_date__gt=datetime.datetime.now(pytz.utc),
                _peer__contains='"user": {"username": "%s"}' % (username))

    # Get all unexpired system-wide notifications
    unexpired_system_notifications = models.Notification.objects.filter(
        # expires_date__gt=datetime.datetime.now(pytz.utc)
        agency__isnull=True,
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
    # models.NotificationMailBox.objects.all().delete()

    if models.NotificationMailBox.objects.count() == 0:
        # Migration code goes here
        print('Starting Notification Mailbox Migration')

        total_count = 0
        for current_profile in models.Profile.objects.all():
            current_profile_username = current_profile.user.username
            current_notifications = get_self_notifications(current_profile_username)
            current_notifications_len = len(current_notifications)
            total_count = total_count + current_notifications_len
            print('==== Migrating {} notifications for user {} ==='.format(current_notifications_len, current_profile_username))

            for current_notification in current_notifications:
                print('{}-{}-{}'.format(current_notification.notification_type, current_notification.message, current_notification.pk))
                # NotificationV2
                notificationv2 = models.NotificationMailBox()
                notificationv2.target_profile = current_profile
                notificationv2.notification_id = current_notification.pk

                # All the flags default to false
                notificationv2.emailed_status = False

                notificationv2.save()

        print('---------')
        print('Total Unexpired Notification Count: {}'.format(total_count))
    else:
        print('Notifications has already been migrated to Mailbox')
