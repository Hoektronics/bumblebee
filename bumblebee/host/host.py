import threading

from bumblebee.host.api.handlers.bots import BotsHandler
from bumblebee.host.api.handlers.jobs import JobsHandler
from bumblebee.host.api.manager import ApiManager
from bumblebee.host.events import HostEvents
from bumblebee.host.framework.events import bind_events
from bumblebee.host.framework.ioc import Resolver


@bind_events
class Host(object):
    def __init__(self):
        self._stop_event = threading.Event()

    def run(self):
        HostEvents.Startup().fire()

        resolver: Resolver = Resolver.get()
        manager: ApiManager = resolver(ApiManager)
        manager.add_handler(resolver(BotsHandler))
        manager.add_handler(resolver(JobsHandler))

        manager.start()

        self._stop_event.wait()

        HostEvents.Shutdown().fire()

    def stop(self):
        self._stop_event.set()
