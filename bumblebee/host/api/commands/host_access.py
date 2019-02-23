from requests import Response

from bumblebee.host.api.rest import RestApi
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.types import Host


class HostAccess(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: RestApi):
        self.config = config
        self.api = api

    def __call__(self):
        request_id = self.config["host_request_id"]

        response: Response = self.api.post(f"/host/requests/{request_id}/access")

        if response.ok:
            json = response.json()
            self.config["access_token"] = json["data"]["access_token"]
            self.config["id"] = json["data"]["host"]["id"]
            self.config["name"] = json["data"]["host"]["name"]

            del self.config["host_request_id"]

            host = Host(
                id=json["data"]["host"]["id"],
                name=json["data"]["host"]["name"]
            )

            AuthFlowEvents.HostMade(host).fire()