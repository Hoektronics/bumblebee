import threading

from bumblebee.host.events import HostEvents
from bumblebee.host.framework.events import bind_events
from bumblebee.host.framework.ioc import Resolver
from bumblebee.host.managers.bots_manager import BotsManager
from bumblebee.host.managers.available_connections_manager import AvailableConnectionsManager


@bind_events
class Host(object):
    def __init__(self,
                 resolver: Resolver,
                 bots_manager: BotsManager,
                 available_connections_manager: AvailableConnectionsManager):
        self.resolver = resolver
        self.bots_manager = bots_manager
        self.available_connections_manager = available_connections_manager

        self._stop_event = threading.Event()

    def run(self):
        HostEvents.Startup().fire()

        self.bots_manager.start()
        self.available_connections_manager.start()

        self._stop_event.wait()

        HostEvents.Shutdown().fire()

    def stop(self):
        self._stop_event.set()
