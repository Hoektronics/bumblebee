from bumblebee.bot_worker import BotWorker
from bumblebee.host import on
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import HostEvents, AuthFlowEvents
from bumblebee.host.events import BotEvents
from bumblebee.host.framework.events import bind_events
from bumblebee.host.framework.ioc import Resolver


@bind_events
class BQClient(object):
    def __init__(self,
                 resolver: Resolver):
        self.resolver = resolver
        self._workers = {}

    @on(AuthFlowEvents.HostRequestMade)
    def _host_request_made(self, event: AuthFlowEvents.HostRequestMade):
        request_id = event.host_request.id

        host_config: HostConfiguration = self.resolver(HostConfiguration)
        server = host_config["server"]

        url = f"{server}/hosts/requests/{request_id}"
        print("Please go here in a web browser to claim this host!")
        print(url)

    @on(HostEvents.Startup)
    def _start(self):
        print("Host startup!")

    @on(HostEvents.Shutdown)
    def _shutdown(self):
        print("Host shutdown!")

    @on(BotEvents.BotAdded)
    def _bot_added(self, event: BotEvents.BotAdded):
        worker = self.resolver(BotWorker, bot=event.bot)

        self._workers[event.bot.id] = worker

    @on(BotEvents.BotRemoved)
    def _bot_removed(self, event):
        print("Bot removed! :(")
        print(event.bot)
