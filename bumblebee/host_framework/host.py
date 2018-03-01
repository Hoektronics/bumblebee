from .api import BotQueueAPI
from .configuration import HostConfiguration
from .events.event import event_manager
from .events import HostEvents


class Host(object):
    def __init__(self, app_name):
        self.app_name = app_name
        self.config = HostConfiguration(self.app_name)
        self.api = BotQueueAPI(self.config)
        self.event_manager = event_manager

    def run(self):
        self.event_manager.fire(HostEvents.Startup)
        self.event_manager.fire(HostEvents.Shutdown)
