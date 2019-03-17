from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.configurations import HostConfiguration


class RefreshAccessToken(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: BotQueueApi):
        self.config = config
        self.api = api

    def __call__(self):
        response = self.api.command("RefreshAccessToken")

        self.config["access_token"] = response["access_token"]
