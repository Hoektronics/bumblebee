from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.types import Host


class ConvertRequestToHost(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: BotQueueApi):
        self.config = config
        self.api = api

    def __call__(self):
        request_id = self.config["host_request_id"]

        response = self.api.command("ConvertRequestToHost", {
            "data": request_id
        })
        
        self.config["access_token"] = response["access_token"]
        self.config["id"] = response["host"]["id"]
        self.config["name"] = response["host"]["name"]

        del self.config["host_request_id"]

        host = Host(
            id=response["host"]["id"],
            name=response["host"]["name"]
        )

        AuthFlowEvents.HostMade(host).fire()