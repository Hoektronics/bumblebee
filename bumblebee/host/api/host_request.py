from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.configurations import HostConfiguration


class HostRequest(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: BotQueueApi):
        self.config = config
        self.api = api

    def __call__(self):
        response = self.api.post("/host/requests")

        request_id = response["data"]["id"]

        self.config["host_request_id"] = request_id
