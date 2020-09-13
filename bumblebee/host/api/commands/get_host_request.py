from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.server import Server


class GetHostRequest(object):
    def __init__(self,
                 server: Server,
                 api: BotQueueApi):
        self._server = server
        self.api = api

    def __call__(self):
        return self.api.command("GetHostRequest", {
            "id": self._server.request_id
        })
