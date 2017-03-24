"""
PubSub
"""


class Observer(object):

    def execute(self):
        pass


class Dispatcher(object):

    def __init__(self):
        self.observer = {

        }

    def publish(self, event_type, **kwargs):
        print('{}-{}'.format(event_type, kwargs))

# Dispatcher Instance
dispatcher = Dispatcher()
