from requests import Response

from bumblebee.host.api.rest import RestApi
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.types import HostRequest


class MakeHostRequest(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: RestApi):
        self.config = config
        self.api = api

    def __call__(self):
        response: Response = self.api.post("/host/requests")

        if response.ok:
            json = response.json()
            host_request = HostRequest(
                id=json["data"]["id"],
                status=json["data"]["status"]
            )

            self.config["host_request_id"] = host_request.id

            AuthFlowEvents.HostRequestMade(host_request).fire()
