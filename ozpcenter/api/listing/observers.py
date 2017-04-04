"""
Observers
"""
import datetime
import pytz

from ozpcenter import models
from ozpcenter.pubsub import Observer
import ozpcenter.api.notification.model_access as notification_model_access


class ListingObserver(Observer):

    def events_to_listen(self):
        return ['listing_created',
                'listing_enabled_status_changed',
                'listing_approval_status_change',
                'listing_private_status_changed',
                'listing_review_created',
                'listing_categories_changed',
                'listing_tags_changed']

    def execute(self, event_type, **kwargs):
        """
        TODO: Finish
        """
        print('message: event_type:{}, kwards:{}'.format(event_type, kwargs))

    def listing_approval_status_change(self, listing=None, profile=None, old_approval_status=None, new_approval_status=None):
        """
        AMLNG-170 - As an Owner I want to receive notice of whether my deletion request has been approved or rejected
        AMLNG-173 - As an Admin I want notification if an owner has cancelled an app that was pending deletion
        AMLNG-380 - As a user, I want to receive notification when a Listing is added to a subscribed category or tag

        State Transitions:
            User Submitted Listings
                {'old_approval_status': 'IN_PROGRESS', 'new_approval_status': 'PENDING'}
            User put Listing in deletion pending
                {'old_approval_status': 'PENDING', 'new_approval_status': 'PENDING_DELETION'}
                {'old_approval_status': 'APPROVED', 'new_approval_status': 'PENDING_DELETION'}
            User undeleted the listing
                {'old_approval_status': 'PENDING_DELETION', 'new_approval_status': 'PENDING'}
            Org Steward APPROVED listing
                {'old_approval_status': 'PENDING', 'new_approval_status': 'APPROVED_ORG'}
            App Mall Steward Rejected Listing
                {'old_approval_status': 'APPROVED_ORG', 'new_approval_status': 'REJECTED')
            App Mall Steward Approved Lising
                {'old_approval_status': 'APPROVED_ORG', 'new_approval_status': 'APPROVED'}
            Listing DELETED
                {'old_approval_status': 'PENDING_DELETION', 'new_approval_status': 'DELETED'}
                {'old_approval_status': 'APPROVED', 'new_approval_status': 'DELETED'}

        Args:
            listing: Listing instance
            profile(Profile Instance): Profile that triggered a change
            approval_status(String): Status
        """
        if new_approval_status == models.Listing.APPROVED and profile.highest_role() != 'APPS_MALL_STEWARD':
            return None
            # raise errors.PermissionDenied('Only an APPS_MALL_STEWARD can mark a listing as APPROVED')
        if new_approval_status == models.Listing.APPROVED_ORG and profile.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
            return None
            # raise errors.PermissionDenied('Only stewards can mark a listing as APPROVED_ORG')
        if new_approval_status == models.Listing.PENDING:
            pass
            # model_access.submit_listing(user, instance)
        if new_approval_status == models.Listing.PENDING_DELETION:
            pass
            # model_access.pending_delete_listing(user, instance)
        if new_approval_status == models.Listing.APPROVED_ORG:
            pass
            # model_access.approve_listing_by_org_steward(user, instance)
        if new_approval_status == models.Listing.APPROVED:
            pass
            # model_access.approve_listing(user, instance)
        if new_approval_status == models.Listing.REJECTED:
            pass
        if new_approval_status == models.Listing.DELETED:
            pass


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
        AMLNG-376 - As a CS, I want to receive notification of Listings submitted for my organization

        Args:
            listing: Listing Instance
            user(Profile Instance): The user that created listing
        """
        pass

    def listing_review_created(self, listing=None):
        """
        AMLNG- 377 - As an owner or CS, I want to receive notification of user rating and reviews

        Args:
            listing: Listing instance
        """
        pass

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
        notification_model_access.create_notification(username,
                                                      now_plus_month,
                                                      message,
                                                      listing)

    def listing_enabled_status_changed(self, listing=None, profile=None, is_enabled=None):
        """
        AMLNG-378 - As a user, I want to receive notification about changes on Listings I've bookmarked

        Args:
            listing: Listing instance
            profile(Profile Instance): Profile that triggered a change
            is_enabled: boolean value
        """
        pass
