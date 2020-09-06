from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.server import Server
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.types import Host


class ConvertRequestToHost(object):
    def __init__(self,
                 server: Server,
                 api: BotQueueApi):
        self._server = server
        self.api = api

    def __call__(self):
        request_id = self._server.request_id

        response = self.api.command("ConvertRequestToHost", {
            "id": request_id
        })

        self._server.access_token = response["access_token"]
        self._server.host_id = response["host"]["id"]
        self._server.host_name = response["host"]["name"]

        del self._server.request_id

        host = Host(
            id=response["host"]["id"],
            name=response["host"]["name"]
        )

        AuthFlowEvents.HostMade(host).fire()
