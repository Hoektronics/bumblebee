from bumblebee.host import on
from bumblebee.host.api.rest import RestApi
from bumblebee.host.api.socket import WebsocketApi
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents, BotEvents, JobEvents
from bumblebee.host.framework.events import bind_events


@bind_events
class BotsHandler(object):
    def __init__(self,
                 config: HostConfiguration,
                 rest: RestApi,
                 socket: WebsocketApi):
        self.config = config
        self.rest = rest
        self.socket = socket
        self._bots = {}

        if "id" in self.config:
            host_id = self.config["id"]
            self.socket.subscribe(f"private-host.{host_id}")

    @on(AuthFlowEvents.HostMade)
    def _subscribe_to_host(self, event: AuthFlowEvents.HostMade):
        host_id = event.host["id"]
        self.socket.subscribe(f"private-host.{host_id}")

    def poll(self):
        response = self.rest.with_token().get("/host/bots")

        if not response.ok:
            return

        json = response.json()

        _bot_ids_seen_in_response = []
        for bot in json["data"]:
            bot_id = bot["id"]

            if bot_id not in self._bots:
                BotEvents.BotAdded(bot).fire()

            if "job" in bot:
                JobEvents.JobAssigned(bot["job"]).fire()

            _bot_ids_seen_in_response.append(bot_id)
            self._bots[bot_id] = bot

        for bot_id in list(self._bots.keys()):
            if bot_id not in _bot_ids_seen_in_response:
                BotEvents.BotRemoved(self._bots[bot_id]).fire()
                del self._bots[bot_id]
