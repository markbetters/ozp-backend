"""
Observers
"""
from ozpcenter.pubsub import Observer


class ListingObserver(Observer):

    def events_to_listen(self):
        return ['listing_created',
                'listing_enabled_status_changed',
                'listing_approval_status_change',
                'listing_private_status_changed',
                'listing_review_created']

    def execute(self, event_type, **kwargs):
        """
        TODO:
        """
        print('message: event_type:{}, kwards:{}'.format(event_type, kwargs))

    def listing_private_status_changed(self, listing=None):
        pass
