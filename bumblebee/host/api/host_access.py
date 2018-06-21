from requests import Response

from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.configurations import HostConfiguration


class HostAccess(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: BotQueueApi):
        self.config = config
        self.api = api

    def __call__(self):
        request_id = self.config["host_request_id"]

        response: Response = self.api.post(f"/host/requests/{request_id}/access")

        if response.ok:
            json = response.json()
            self.config["access_token"] = json["access_token"]
            del self.config["host_request_id"]