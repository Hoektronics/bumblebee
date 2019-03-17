from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.configurations import HostConfiguration


class GetHostRequest(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: BotQueueApi):
        self.config = config
        self.api = api

    def __call__(self):
        request_id = self.config["host_request_id"]

        return self.api.command("GetHostRequest", {
            "id": request_id
        })
