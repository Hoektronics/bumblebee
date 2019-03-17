from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.types import HostRequest


class CreateHostRequest(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: BotQueueApi):
        self.config = config
        self.api = api

    def __call__(self):
        response = self.api.command("CreateHostRequest")
        
        host_request = HostRequest(
            id=response["id"],
            status=response["status"]
        )

        self.config["host_request_id"] = host_request.id

        AuthFlowEvents.HostRequestMade(host_request).fire()
