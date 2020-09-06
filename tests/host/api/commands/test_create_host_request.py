from unittest.mock import Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.create_host_request import CreateHostRequest
from bumblebee.host.api.server import Server
from bumblebee.host.events import AuthFlowEvents


class TestCreateHostRequest(object):
    def test_host_request_sets_host_request_id(self, resolver, fakes_events):
        fakes_events.fake(AuthFlowEvents.HostRequestMade)

        server = resolver(Server, url="https://server/")
        resolver.instance(server)

        api = Mock(BotQueueApi)
        api.command.return_value = {
                "id": 1,
                "status": "requested"
            }
        resolver.instance(api)

        make_host_request = resolver(CreateHostRequest)

        make_host_request()

        api.command.assert_called_once_with("CreateHostRequest")

        assert server.request_id == 1
        assert fakes_events.fired(AuthFlowEvents.HostRequestMade).once()

        event: AuthFlowEvents.HostRequestMade = fakes_events.fired(AuthFlowEvents.HostRequestMade).event
        assert event.host_request.id == 1
        assert event.host_request.status == "requested"
