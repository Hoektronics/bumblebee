from requests import Response

from bumblebee.host.api.rest import RestApi
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents


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
            request_id = json["data"]["id"]
            self.config["host_request_id"] = request_id

            AuthFlowEvents.HostRequestMade(json["data"]).fire()
