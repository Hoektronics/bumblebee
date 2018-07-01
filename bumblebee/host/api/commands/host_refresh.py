from requests import Response

from bumblebee.host.api.rest import RestApi
from bumblebee.host.configurations import HostConfiguration


class HostRefresh(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: RestApi):
        self.config = config
        self.api = api

    def __call__(self):
        response: Response = self.api.with_token().post("/host/refresh")

        if response.ok:
            json = response.json()
            self.config["access_token"] = json["access_token"]
