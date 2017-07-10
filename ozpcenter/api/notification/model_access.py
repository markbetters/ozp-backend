"""
Model access

https://github.com/aml-development/ozp-documentation/wiki/Notifications

Notification Type
    SYSTEM = 'system'  # System-wide Notifications
    AGENCY = 'agency'  # Agency-wide Notifications
    AGENCY_BOOKMARK = 'agency_bookmark'  # Agency-wide Bookmark Notifications # Not requirement (erivera 20160621)
    LISTING = 'listing'  # Listing Notifications
    PEER = 'peer'  # Peer to Peer Notifications
    PEER_BOOKMARK = 'peer_bookmark'  # Peer to Peer Bookmark Notifications
    SUBSCRIPTION = 'subscription' # Category and Tag Subscription Notification

Group Target
    ALL = 'all'  # All users
    STEWARDS = 'stewards'
    APP_STEWARD = 'app_steward'
    ORG_STEWARD = 'org_steward'
    USER = 'user'

=====Notification Type=====

                +--> SystemWide
                |
                +--> AgencyWide
                |
                +--> AgencyWideBookmark
                |
Notification +------+--> Listing
                |   |
                |   +--> ListingReview
                |   |
                |   +--> ListingPrivateStatus
                |   |
                |   +--> PendingDeletionRequest
                |   |
                |   +--> PendingDeletionCancellation
                |   |
                |   +--> ListingSubmission
                |
                +--> Peer
                |
                +--> PeerBookmark
                |
                +--> CategorySubscription
                |
                +--> TagSubscription

=====Vocab=====
Target: is a Profile that should receive a notification
Target List: A list of Profiles that should receive notifications
Direct notification: The notification is produced by an action that the user does.
In-direct Notification: The notification is produced by the observing a user action.
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
from ozpcenter.models import Subscription


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

        'add_subscription_notification',
        'change_subscription_notification',
        'delete_subscription_notification'
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

        'add_subscription_notification',
        'change_subscription_notification',
        'delete_subscription_notification'
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

        'add_subscription_notification',
        'change_subscription_notification',
        'delete_subscription_notification'
        ]
}


def check_notification_permission(profile_instance, action, notification_type):
    """
    Check to see if user has permission

    Args:
        profile_instance(Profile): Profile Instance
        action(string): add/change/delete
        notification_type(string): notification type
    Return:
        True or PermissionDenied Exception
    """
    profile_role = profile_instance.highest_role()
    assert (profile_role in permission_dict), 'Profile group {} not found in permissions'.format(profile_role)

    user_action = '{}_{}_notification'.format(action, notification_type)

    profile_permission_list = permission_dict[profile_role]

    if user_action not in profile_permission_list:
        raise errors.PermissionDenied('Profile does not have [{}] permissions'.format(user_action))
    return True


class NotificationBase(object):
    """
    Process:
        Init NotificationBase Super Class Object
        Set sender_profile and entities list
        Validate sender_profile and entities list
        Do Global Permission Check

        Notify
            Validate expires_date, message
    """

    def set_sender_and_entity(self, sender_profile_username, entity, metadata=None):
        """
        Set Sender Profile, entity object, metadata

        Args:
            sender_profile_username(string): Sender's Profile username (normally the request profile)
            entity(object):
        """
        assert (sender_profile_username is not None), 'Sender Profile Username is necessary'

        self.sender_profile_username = sender_profile_username
        self.sender_profile = generic_model_access.get_profile(sender_profile_username)
        self.entity = entity
        self.metadata = metadata

    def check_local_permission(self, entity):
        return True

    def permission_check(self):
        """
        Global and Local check
        """
        check_notification_permission(self.sender_profile, 'add', self.get_notification_db_type())
        self.check_local_permission(self.entity)

    def get_notification_db_type(self):
        raise RuntimeError('Not Implemented')

    def get_target_list(self):
        raise RuntimeError('Not Implemented')

    def get_entity_id(self):
        """
        self.entity is a Model Type Instance if not overrided
        """
        if self.entity:
            return self.entity.id
        else:
            return None

    def get_group_target(self):
        return Notification.ALL

    def notify(self, expires_date, message):
        assert (expires_date is not None), 'Expires Date is necessary'
        assert (message is not None), 'Message is necessary'
        self.permission_check()

        notification = Notification(
            expires_date=expires_date,
            author=self.sender_profile,
            message=message)

        notification_type = self.get_notification_db_type()
        notification.notification_type = notification_type
        notification.entity_id = self.get_entity_id()
        notification.group_target = self.get_group_target()

        if notification_type == Notification.AGENCY or notification_type == Notification.AGENCY_BOOKMARK:
            notification.agency = self.entity
        elif notification_type == Notification.LISTING:
            notification.listing = self.entity
        elif notification_type == Notification.PEER or notification_type == Notification.PEER_BOOKMARK:
            notification.peer = self.metadata

        notification.save()

        target_list = self.get_target_list()

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


class SystemWideNotification(NotificationBase):
    """
    AMLNG-395 - SystemWide
        As a user, I want to receive System-Wide Notifications
    Targets: All Users
    Permission Constraint: Only APP_MALL_STEWARDs can send notifications
    Invoked: Directly
    """

    def get_notification_db_type(self):
        return Notification.SYSTEM

    def get_target_list(self):
        """
        Get every profile
        """
        return Profile.objects.all()


class AgencyWideNotification(NotificationBase):
    """
    AMLNG-398 - AgencyWide
        As a user, I want to receive Agency-Wide Notifications
    Targets: All Users in an agency
    Permission Constraint: Only APP_MALL_STEWARDs, ORG_STEWARDs can send notifications
    Invoked: Directly
    """

    def get_notification_db_type(self):
        return Notification.AGENCY

    def get_target_list(self):
        """
        Get every profile that belongs to an organization and get all stewards for that organization
        """
        return Profile.objects.filter(Q(organizations__in=[self.entity]) |
                                      Q(stewarded_organizations__in=[self.entity])).all()


class AgencyWideBookmarkNotification(NotificationBase):
    """
    AMLNG-398 - AgencyWide Bookmark
        As a user, I want to receive Agency-Wide Notifications
    Targets: All Users in an agency
    Permission Constraint: Only APP_MALL_STEWARDs, ORG_STEWARDs can send notifications
    Invoked: Directly
    """

    def get_notification_db_type(self):
        return Notification.AGENCY_BOOKMARK

    def get_target_list(self):
        """
        Get every profile that belongs to an organization and get all stewards for that organization
        """
        return Profile.objects.filter(Q(organizations__in=[self.entity]) |
                                      Q(stewarded_organizations__in=[self.entity])).all()


class ListingNotification(NotificationBase):
    """
    AMLNG-396 - Listing Notifications
    Targets: All users that bookmarked listing
    Permission Constraint: Only APP_MALL_STEWARDs and ORG_STEWARDs or owners of listing can send notifications
    Invoked: Directly
    """

    def get_notification_db_type(self):
        return Notification.LISTING

    def get_target_list(self):
        """
        Get every profile that has bookmarked that listing
        """
        owner_id_list = ApplicationLibraryEntry.objects.filter(listing__in=[self.entity],
                                                               listing__isnull=False,
                                                               listing__is_enabled=True,
                                                               listing__approval_status=Listing.APPROVED,
                                                               listing__is_deleted=False).values_list('owner', flat=True).distinct()
        return Profile.objects.filter(id__in=owner_id_list, listing_notification_flag=True).all()

    def check_local_permission(self, entity):
        if self.sender_profile.highest_role() in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
            return True

        if self.sender_profile not in entity.owners.all():
            raise errors.PermissionDenied('Cannot create a notification for a listing you do not own')
        else:
            return True
        return False


class PeerNotification(NotificationBase):
    """
    Peer
        As a user, I want to receive notification when someone send a message to me
    Targets: User Given Target
    Permission Constraint:
    """

    def get_notification_db_type(self):
        return Notification.PEER

    def get_group_target(self):
        return Notification.USER

    def get_target_list(self):
        entities_id = [entity.id for entity in [self.entity]]
        return Profile.objects.filter(id__in=entities_id).all()


class PeerBookmarkNotification(NotificationBase):
    """
    AMLNG-381 - PeerBookmark
        As a user, I want to receive notification when someone shares a folder with me
    Targets: User Given Target
    Permission Constraint:  Must be owner of shared folder to send

    Test Case:
        Logged on as jones
        Shared a folder with aaronson
        Logged on as aaronson
        RESULTS: aaronson has a new notification added to the notification count.Add folder button is present and adds the shared folder to HuD screen.
    """

    def get_notification_db_type(self):
        return Notification.PEER_BOOKMARK

    def get_group_target(self):
        return Notification.USER

    def get_target_list(self):
        entities_id = [entity.id for entity in [self.entity]]
        return Profile.objects.filter(id__in=entities_id).all()


class ListingReviewNotification(NotificationBase):  # Not Verified
    """
    AMLNG-377 - ListingReview
        As an owner or CS, I want to receive notification of user rating and reviews
    Targets: Users that ___
    Invoked: In-directly

    Test Case:
        Description - Verify the CS and listing owner receives a notification when the review is added or modified.
        *Pre-req*- Add aaronson as listing owner to Airmail.
        Log on as syme (minipax)
        Deleted, Added and Modified review on Airmail ( minitru)
        Log on as wsmith (minitru-org steward)
        EXPECTED RESULTS - At least two notifications should display for wsmith.
        Log on as aaronson
        EXPECTED RESULTS - At least two notifications should display for aaronson.
    """

    def get_notification_db_type(self):
        return Notification.LISTING

    def get_group_target(self):
        return Notification.USER

    def get_target_list(self):
        current_listing = self.entity

        target_set = set()

        for owner in current_listing.owners.filter(listing_notification_flag=True).all():
            target_set.add(owner)

        current_listing_agency_id = current_listing.agency.id

        for steward in Profile.objects.filter(stewarded_organizations__in=[current_listing_agency_id], listing_notification_flag=True).all():
            target_set.add(steward)

        return list(target_set)


class ListingPrivateStatusNotification(NotificationBase):
    """
    AMLNG-383 - ListingPrivateStatus
        As a owner, I want to notify users who have bookmarked my listing when the
        listing is changed from public to private and vice-versa
    Permission Constraint: Only APP_MALL_STEWARDs and ORG_STEWARDs or owners of listing can
    Targets: Users that bookmarked listing
    Invoked: In-directly

    Test Case:
        Bookmarked an app listing in my own org
        Went to Bookmarked App Listing Quick View Modal | Send Notifications | Sent a notification
        RESULTS - I received the notification
        Bookmarked an app listing that did not belong to the org I was in
        Went to Bookmarked App Listing  Quick View Modal | Send Notifications | Sent a notification
        RESULTS - I received the notification
    """

    def get_notification_db_type(self):
        return Notification.LISTING

    def get_target_list(self):
        owner_id_list = ApplicationLibraryEntry.objects.filter(listing__in=[self.entity],
                                                               listing__isnull=False,
                                                               listing__approval_status=Listing.APPROVED,
                                                               listing__is_enabled=True,
                                                               listing__is_deleted=False).values_list('owner', flat=True).distinct()
        return Profile.objects.filter(id__in=owner_id_list, listing_notification_flag=True).all()

    def check_local_permission(self, entity):
        if self.sender_profile.highest_role() in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
            return True

        if self.sender_profile not in entity.owners.all():
            raise errors.PermissionDenied('Cannot create a notification for a listing you do not own')
        else:
            return True
        return False


class PendingDeletionRequestNotification(NotificationBase):  # Not Verified
    """
    AMLNG-170 - PendingDeletionRequest
        As an Owner I want to receive notice of whether my deletion request has been approved or rejected
    Targets: Users that ___
    Invoked: In-directly

    This event occurs when
        Listing DELETED - Steward approved deletion
            PENDING_DELETION --> DELETED

        User undeleted the listing - Steward rejects deletion
            PENDING_DELETION --> PENDING

    Test Case:
        Logged on as jones
        Set Test Notification Listing to Pend for Deletion state
        Logged on as minitrue Org Content Steward- julia
        Approved the deletion
        Logged on as jones
        RESULTS The notification launched = Test Notification Listing listing was approved for deletion by steward
    """

    def get_notification_db_type(self):
        return Notification.LISTING

    def get_target_list(self):
        current_listing = self.entity
        return current_listing.owners.filter(listing_notification_flag=True).all().distinct()


class PendingDeletionCancellationNotification(NotificationBase):  # Not Verified
    """
    AMLNG-173 - PendingDeletionCancellation
        As an cs I want a notification if an owner has cancelled an app
        that was pending deletion

    This event occurs when
        User undeleted the listing
            PENDING_DELETION --> PENDING

    Test Case:
        Set Test Notification Listing to Pend for Deletion Status
        Logged on as jones ( owner of <Test Notification> Listing)
        Undeleted the Test Notification Listing
        Logged on as Org Content Steward - julia
        RESULTS - Notificaiton launched = Listing Owner cancelled deletion of Test Notification Listing listing
    """

    def get_notification_db_type(self):
        return Notification.LISTING

    def get_target_list(self):
        current_listing = self.entity
        current_listing_agency_id = current_listing.agency.id
        return Profile.objects.filter(stewarded_organizations__in=[current_listing_agency_id], listing_notification_flag=True).all().distinct()


class ListingSubmissionNotification(NotificationBase):
    """
    AMLNG-376 - ListingSubmission
        As a CS, I want to receive notification of Listings submitted for my organization
    Targets: Listing Agency ORG_STEWARDs
    Invoked: In-directly

    This event occurs when
        User Submitted Listings
            IN_PROGRESS --> PENDING

    a = Listing.objects.last(); a.approval_status = Listing.IN_PROGRESS; a.save()

    Test Case:
        Logged into Apps Mall as jones ( minitrue)
        Submitted a new listing using org minitrue.
        Logged into Apps mall as CS - julia (minitrue)
        RESULTS - Notification displays = Test Notification Listing listing was submitted
    """

    def get_group_target(self):
        return Notification.ORG_STEWARD

    def get_notification_db_type(self):
        return Notification.LISTING

    def get_target_list(self):
        current_listing = self.entity
        current_listing_agency_id = current_listing.agency.id
        return Profile.objects.filter(stewarded_organizations__in=[current_listing_agency_id], listing_notification_flag=True).all().distinct()


class TagSubscriptionNotification(NotificationBase):  # Not Verified
    """
    AMLNG-392 - TagSubscription
        As a user, I want to receive notification when a Listing is added to a subscribed tag
    Targets: Users that ___
    Invoked: In-directly
    """

    def get_notification_db_type(self):
        return Notification.SUBSCRIPTION

    def get_target_list(self):
        subscription_entries = Subscription.objects.filter(entity_type='tag', entity_id__in=list(self.metadata))
        target_profiles = set()
        for subscription_entry in subscription_entries:
            target_profile = subscription_entry.target_profile
            if target_profile.subscription_notification_flag:
                target_profiles.add(target_profile)

        return list(target_profiles)


class CategorySubscriptionNotification(NotificationBase):  # Not Verified
    """
    AMLNG-380 - CategorySubscription
        As a user, I want to receive notification when a Listing is added to a subscribed category
    Targets: Users that are subscribed to category
    Invoked: In-directly
        Should occur when a user submits a listing with a category and listing gets approved,
            it should send out notifications for users that have that category subscribed and has the Subscription Preference Flag to True
        Should occur when a published listing add new category,
            it should send out notifications for users that have that category subscribed and has the Subscription Preference Flag to True

    Test Case:
        Logged on as jones
        Subscribed to Finance
        Logged on as big brother
        Add any Listing to Finance
        Logged on as jones
        RESULTS- Notification "A new listing in category Finance"
    """

    def get_notification_db_type(self):
        return Notification.SUBSCRIPTION

    def get_target_list(self):
        subscription_entries = Subscription.objects.filter(entity_type='category', entity_id__in=list(self.metadata))
        target_profiles = set()
        for subscription_entry in subscription_entries:
            target_profile = subscription_entry.target_profile
            if target_profile.subscription_notification_flag:
                target_profiles.add(target_profile)

        return list(target_profiles)


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
        expires_date__gt=datetime.datetime.now(pytz.utc)).order_by('-created_date')

    if for_user:
        unexpired_system_notifications = unexpired_system_notifications.filter(agency__isnull=True,
                                              listing__isnull=True,
                                              _peer__isnull=True).order_by('-created_date')

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
        expires_date__lt=datetime.datetime.now(pytz.utc)).order_by('-created_date')
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

    notifications_mailbox = NotificationMailBox.objects.filter(target_profile=get_self(username), notification__expires_date__gt=datetime.datetime.now(pytz.utc)).all()
    return notifications_mailbox


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
                        group_target=Notification.ALL,
                        notification_type=None,
                        entities=None):
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
    if notification_type == 'ListingSubmissionNotification':
        notification_instance = ListingSubmissionNotification()
        notification_instance.set_sender_and_entity(author_username, listing)

    elif notification_type == 'ListingReviewNotification':
        notification_instance = ListingReviewNotification()
        notification_instance.set_sender_and_entity(author_username, listing)

    elif notification_type == 'PendingDeletionRequestNotification':
        notification_instance = PendingDeletionRequestNotification()
        notification_instance.set_sender_and_entity(author_username, listing)

    elif notification_type == 'PendingDeletionCancellationNotification':
        notification_instance = PendingDeletionCancellationNotification()
        notification_instance.set_sender_and_entity(author_username, listing)

    elif notification_type == 'CategorySubscriptionNotification':
        notification_instance = CategorySubscriptionNotification()
        notification_instance.set_sender_and_entity(author_username, listing, entities)

    elif notification_type == 'TagSubscriptionNotification':
        notification_instance = TagSubscriptionNotification()
        notification_instance.set_sender_and_entity(author_username, listing, entities)

    elif listing is not None:
        notification_instance = ListingNotification()
        notification_instance.set_sender_and_entity(author_username, listing)

    elif agency is not None:
        notification_instance = AgencyWideNotification()
        notification_instance.set_sender_and_entity(author_username, agency)

    elif peer is not None:
        notification_instance = PeerNotification()
        try:
            if peer and 'folder_name' in peer:
                notification_instance = PeerBookmarkNotification()
        except ValueError:
            # Ignore Value Errors
            pass
        notification_instance.set_sender_and_entity(author_username, peer_profile, peer)
    else:
        notification_instance = SystemWideNotification()
        notification_instance.set_sender_and_entity(author_username, None)

    notification = notification_instance.notify(expires_date, message)
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

    check_notification_permission(user, 'change', notification_instance.notification_type)

    notification_instance.expires_date = expires_date
    notification_instance.save()
    return notification_instance


def dismiss_notification_mailbox(notification_mailbox_instance, username):
    """
    Dismissed a Notification Mailbox entry

    It deletes the Mailbox Entry for user

    Args:
        notification_mailbox_instance (NotificationMailBox): notification_mailbox_instance
        username (string)

    Return:
        bool: Notification Mailbox Dismissed
    """
    profile_instance = get_self(username)
    NotificationMailBox.objects.filter(target_profile=profile_instance, pk=notification_mailbox_instance.id).delete()
    return True
