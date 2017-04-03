import logging
import threading
import socket
from datetime import datetime

from celery import signals, states

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class CeleryMonitorThread(threading.Thread):
    '''
    Monitors a Celery app. Keeps track of pending tasks.
    Exposes idle and active events.
    '''

    def __init__(self, app):
        super(CeleryMonitorThread, self).__init__()

        self.app = app
        self.state = app.events.State()
        self.stop_requested = False

        self.pending = 0
        self.idle = threading.Event()
        self.idle.set()
        self.active = threading.Event()

    def on_event(self, event):
        # maintain state
        self.state.event(event)

        # only need to update state when something relevant to pending tasks is happening
        check_states = ['task-received','task-started','task-succeeded','task-failed','task-revoked']
        if not event['type'] in check_states:
            return

        active = len(self.immediate_pending_tasks) > 0

        # switch signals if needed
        if active and self.idle.is_set():
            self.idle.clear()
            self.active.set()
        elif not active and self.active.is_set():
            self.idle.set()
            self.active.clear()

    @property
    def pending_tasks(self):
        tasks = self.state.tasks.values()
        return [t for t in tasks if t.state in states.UNREADY_STATES]

    @property
    def immediate_pending_tasks(self):
        now = datetime.utcnow().isoformat()
        return [t for t in self.pending_tasks if not t.eta or t.eta < now]

    def run(self):
        with self.app.connection() as connection:
            recv = self.app.events.Receiver(connection, handlers={
                '*': self.on_event,
            })

            # we want to be able to stop from outside
            while not self.stop_requested:
                try:
                    # use timeout so we can monitor if we should stop
                    recv.capture(limit=None, timeout=.5, wakeup=False)
                except socket.timeout:
                    pass

    def stop(self):
        self.stop_requested = True
