from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.server import Server
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.types import HostRequest


class CreateHostRequest(object):
    def __init__(self,
                 server: Server,
                 api: BotQueueApi):
        self._server = server
        self.api = api

    def __call__(self):
        response = self.api.command("CreateHostRequest")
        
        host_request = HostRequest(
            id=response["id"],
            status=response["status"],
            server=self._server.url
        )

        self._server.request_id = host_request.id

        AuthFlowEvents.HostRequestMade(host_request).fire()
