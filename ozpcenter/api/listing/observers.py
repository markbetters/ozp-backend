"""
Observers
"""
import datetime
import pytz

from ozpcenter import models
from ozpcenter.pubsub import Observer
from ozpcenter.models import Notification
import ozpcenter.api.notification.model_access as notification_model_access


class ListingObserver(Observer):

    def events_to_listen(self):
        return ['listing_created',
                'listing_enabled_status_changed',
                'listing_approval_status_change',
                'listing_private_status_changed',
                'listing_review_created',
                'listing_review_changed',
                'listing_categories_changed',
                'listing_tags_changed',
                'listing_changed']

    def execute(self, event_type, **kwargs):
        """
        TODO: Finish
        """
        print('message: event_type:{}, kwards:{}'.format(event_type, kwargs))

    def listing_approval_status_change(self, listing=None, profile=None, old_approval_status=None, new_approval_status=None):
        """
        Listing Approval Status Change

        State Transitions:
            {Action}
                {old_approval_status} --> {new_approval_status}

            User Submitted Listings
                IN_PROGRESS --> PENDING

            User put Listing in deletion pending
                PENDING --> PENDING_DELETION
                APPROVED --> PENDING_DELETION

            User undeleted the listing
                PENDING_DELETION --> PENDING

            Org Steward APPROVED listing
                PENDING --> APPROVED_ORG

            App Mall Steward Rejected Listing
                APPROVED_ORG --> REJECTED

            App Mall Steward Approved Lising
                APPROVED_ORG --> APPROVED

            Listing DELETED - Steward Approved deletion
                PENDING_DELETION --> DELETED
                APPROVED --> DELETED

        AMLNG-170 - As an Owner I want to receive notice of whether my deletion request has been approved or rejected
        AMLNG-173 - As an Admin I want notification if an owner has cancelled an app that was pending deletion
        AMLNG-380 - As a user, I want to receive notification when a Listing is added to a subscribed category or tag

        Args:
            listing: Listing instance
            profile(Profile Instance): Profile that triggered a change
            approval_status(String): Status
        """
        username = profile.user.username
        now_plus_month = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=30)

        # AMLNG-376 - ListingSubmission
        if (old_approval_status == models.Listing.IN_PROGRESS and
                new_approval_status == models.Listing.PENDING):
            message = '{} listing was submitted'.format(listing.title)
            notification_model_access.create_notification(author_username=username,
                                                          expires_date=now_plus_month,
                                                          message=message,
                                                          listing=listing,
                                                          group_target=Notification.ORG_STEWARD,
                                                          notification_type='ListingSubmissionNotification')

        # AMLNG-173 - PendingDeletionCancellation
        if profile in listing.owners.all():  # Check to see if current profile is owner of listing
            if (old_approval_status == models.Listing.PENDING_DELETION and
                    new_approval_status == models.Listing.PENDING):
                message = 'Listing Owner cancelled deletion of {} listing'.format(listing.title)
                notification_model_access.create_notification(author_username=username,
                                                              expires_date=now_plus_month,
                                                              message=message,
                                                              listing=listing,
                                                              group_target=Notification.ORG_STEWARD,
                                                              notification_type='PendingDeletionCancellationNotification')

        # AMLNG-170 - PendingDeletionRequest
        elif profile.highest_role() in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
            if (old_approval_status == models.Listing.PENDING_DELETION and
                    new_approval_status == models.Listing.DELETED):
                message = '{} listing was approved for deletion by steward'.format(listing.title)

                notification_model_access.create_notification(author_username=username,
                                                              expires_date=now_plus_month,
                                                              message=message,
                                                              listing=listing,
                                                              group_target=Notification.USER,
                                                              notification_type='PendingDeletionRequestNotification')

            if (old_approval_status == models.Listing.PENDING_DELETION and
                    new_approval_status == models.Listing.PENDING):
                message = '{} listing was rejected for deletion by steward'.format(listing.title)

                notification_model_access.create_notification(author_username=username,
                                                              expires_date=now_plus_month,
                                                              message=message,
                                                              listing=listing,
                                                              group_target=Notification.USER,
                                                              notification_type='PendingDeletionRequestNotification')

    def listing_categories_changed(self, listing=None, profile=None, old_categories=None, new_categories=None):
        """
        AMLNG-380 - As a user, I want to receive notification when a Listing is added to a subscribed category

        Args:
            listing: Listing instance
            profile(Profile Instance): Profile that triggered a change
            old_categories: List of category instances
            new_categories: List of category instances
        """
        pass

    def listing_tags_changed(self, listing=None, profile=None, old_tags=None, new_tags=None):
        """
        AMLNG-392 - As a user, I want to receive notification when a Listing is added to a subscribed tag

        Args:
            listing: Listing instance
            profile(Profile Instance): Profile that triggered a change
            old_tags: List of Tag instances
            new_tags: List of Tag instances
        """
        pass

    def listing_created(self, listing=None, profile=None):
        """
        Args:
            listing: Listing Instance
            user(Profile Instance): The user that created listing
        """
        pass

    def listing_changed(self, listing=None, profile=None, change_details=None):
        """
        AMLNG-378 - As a user, I want to receive notification about changes on Listings I've bookmarked

        Args:
            listing: Listing Instance
            user(Profile Instance): The user that created listing
        """
        username = profile.user.username

        message = '{} listing was changed. The following fields changed: {}'.format(listing.title, [change_detail['field_name'] for change_detail in change_details])

        now_plus_month = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=30)
        notification_model_access.create_notification(author_username=username,
                                                      expires_date=now_plus_month,
                                                      message=message,
                                                      listing=listing,
                                                      group_target=Notification.USER)

    def listing_review_created(self, listing=None, profile=None, rating=None, text=None):
        """
        AMLNG- 377 - As an owner or CS, I want to receive notification of user rating and reviews

        Args:
            listing: Listing instance
        """
        username = profile.user.username
        now_plus_month = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=30)

        message = 'User has rated listing [{}] {} stars'.format(listing.title, rating)
        notification_model_access.create_notification(author_username=username,
                                                      expires_date=now_plus_month,
                                                      message=message,
                                                      listing=listing,
                                                      notification_type='ListingReviewNotification')

    def listing_review_changed(self, listing=None, profile=None, rating=None, text=None):
        """
        AMLNG- ??? - As an owner or CS, I want to receive notification of user rating and reviews

        Args:
            listing: Listing instance
        """
        username = profile.user.username
        now_plus_month = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=30)

        message = 'User has changed rating for listing [{}] to {} stars'.format(listing.title, rating)
        notification_model_access.create_notification(author_username=username,
                                                      expires_date=now_plus_month,
                                                      message=message,
                                                      listing=listing,
                                                      notification_type='ListingReviewNotification')

    def listing_private_status_changed(self, listing=None, profile=None, is_private=None):
        """
        AMLNG-383 - As a owner, I want to notify users who have bookmarked my listing when the
            listing is changed from public to private and vice-versa

        Args:
            listing: Listing instance
            profile(Profile Instance): Profile that triggered a change ()
            is_private: boolean value
        """
        username = profile.user.username

        message = None

        if is_private:
            message = '{} was changed to be a private listing '.format(listing.title)
        else:
            message = '{} was changed to be a public listing '.format(listing.title)

        now_plus_month = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=30)
        notification_model_access.create_notification(author_username=username,
                                                      expires_date=now_plus_month,
                                                      message=message,
                                                      listing=listing,
                                                      group_target=Notification.USER)

    def listing_enabled_status_changed(self, listing=None, profile=None, is_enabled=None):
        """


        Args:
            listing: Listing instance
            profile(Profile Instance): Profile that triggered a change
            is_enabled: boolean value
        """
        pass
