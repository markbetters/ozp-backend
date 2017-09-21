"""
Observers
"""
from ozpcenter.pubsub import Observer
# import ozpcenter.api.notification.model_access as notification_model_access


class AuthObserver(Observer):

    def events_to_listen(self):
        return ['profile_created']

    def execute(self, event_type, **kwargs):
        print('AuthObserver message: event_type:{}, kwards:{}'.format(event_type, kwargs))

    def profile_created(self, profile=None):
        """
        When a new profile is created,  fill the user's notification 'mailbox' up with unread system-wide unread notifications

        Args:
            listing: Listing instance
        """
        pass

    def listing_owner_certificate_expired(self, profile=None):
        """
        AMLNG-384
            As a owner, I want myself and CS to be notified when one of the Listing owner's certificates expire
        """
        pass
