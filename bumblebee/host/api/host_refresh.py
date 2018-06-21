from requests import Response

from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.configurations import HostConfiguration


class AccessTokenNotFound(Exception):
    pass


class HostRefresh(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: BotQueueApi):
        self.config = config
        self.api = api

    def __call__(self):
        if "access_token" not in self.config:
            raise AccessTokenNotFound("Access token not found in host configuration")

        response: Response = self.api.with_token().post("/host/refresh")

        if response.ok:
            json = response.json()
            self.config["access_token"] = json["access_token"]
