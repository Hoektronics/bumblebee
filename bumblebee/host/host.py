import threading

from bumblebee.host.framework.logging import HostLogging

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
                 available_connections_manager: AvailableConnectionsManager,
                 host_logging: HostLogging):
        self.resolver = resolver
        self.bots_manager = bots_manager
        self.available_connections_manager = available_connections_manager
        self.host_logger = host_logging.get_logger('Host')

        self._stop_event = threading.Event()

    def run(self):
        self.host_logger.info("Starting host run method")
        HostEvents.Startup().fire()

        self.host_logger.info("Starting Bots Manager")
        self.bots_manager.start()
        self.host_logger.info("Starting Available Connections Manager")
        self.available_connections_manager.start()

        self._stop_event.wait()
        self.host_logger.info("Host told to shutdown")

        HostEvents.Shutdown().fire()
        self.host_logger.info("Finishing host run method")

    def stop(self):
        self._stop_event.set()
