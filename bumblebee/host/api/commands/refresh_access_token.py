from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.server import Server
from bumblebee.host.configurations import HostConfiguration


class RefreshAccessToken(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: BotQueueApi,
                 server: Server):
        self.config = config
        self.api = api
        self._server = server

    def __call__(self):
        response = self.api.command("RefreshAccessToken")

        self._server.access_token = response["access_token"]
