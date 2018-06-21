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

        if response.ok:
            json = response.json()
            request_id = json["data"]["id"]
            self.config["host_request_id"] = request_id