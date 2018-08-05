from time import sleep

from bumblebee.host.api.handlers.bots import BotsHandler
from bumblebee.host.api.manager import ApiManager
from bumblebee.host.events import HostEvents
from bumblebee.host.framework.events import bind_events
from bumblebee.host.framework.ioc import Resolver


@bind_events
class Host(object):
    def run(self):
        HostEvents.Startup().fire()

        resolver: Resolver = Resolver.get()
        manager: ApiManager = resolver(ApiManager)
        manager.add_handler(resolver(BotsHandler))

        manager.start()

        sleep(1000)

        HostEvents.Shutdown().fire()
