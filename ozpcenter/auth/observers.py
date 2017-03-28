"""
Observers
"""
from ozpcenter.pubsub import Observer
# import ozpcenter.api.notification.model_access as notification_model_access


class AuthObserver(Observer):

    def events_to_listen(self):
        return ['profile_created']

    def execute(self, event_type, **kwargs):
        """
        TODO: Finish
        """
        print('AuthObserver message: event_type:{}, kwards:{}'.format(event_type, kwargs))

        if event_type == 'profile_created':
            self.profile_created(**kwargs)

    def profile_created(self, profile=None):
        """
        When a new profile is created,  fill the user's notification 'mailbox' up with unread system-wide unread notifications

        Args:
            listing: Listing instance
        """
        pass
