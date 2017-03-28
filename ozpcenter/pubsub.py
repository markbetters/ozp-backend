"""
Dispatcher
"""


class Observer(object):

    def events_to_listen(self):
        "The base classes should funtion should return a list of topics to listen to"
        raise NotImplementedError()

    def execute(self, event_type, **kwargs):
        raise NotImplementedError()


class Dispatcher(object):

    def __init__(self):
        self.observers = {}

    def register(self, observer_class):
        observer_name = observer_class.__name__

        if observer_name not in self.observers:
            self.observers[observer_name] = observer_class()  # Making instance of class

    def publish(self, event_type, **kwargs):
        for key in self.observers:
            class_object = self.observers[key]
            if event_type in class_object.events_to_listen():
                class_object.execute(event_type, **kwargs)

# Import Observers
import ozpcenter.auth.observers as auth_observers
import ozpcenter.api.listing.observers as listing_observers

# Dispatcher Instance
dispatcher = Dispatcher()

dispatcher.register(listing_observers.ListingObserver)
dispatcher.register(auth_observers.AuthObserver)
