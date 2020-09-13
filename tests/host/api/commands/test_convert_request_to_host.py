from unittest.mock import Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.convert_request_to_host import ConvertRequestToHost
from bumblebee.host.api.server import Server
from bumblebee.host.events import AuthFlowEvents


class TestConvertRequestToHost(object):
    def test_accepting_host_request(self, resolver, fakes_events):
        fakes_events.fake(AuthFlowEvents.HostMade)

        server = resolver(Server, url="https://server/")
        resolver.instance(server)

        server.request_id = "request_id"

        api = Mock(BotQueueApi)
        api.command.return_value = {
            "access_token": "my_token",
            "host": {
                "id": 1,
                "name": "Test Host"
            }
        }
        resolver.instance(api)

        host_access = resolver(ConvertRequestToHost)

        host_access()

        api.command.assert_called_once_with("ConvertRequestToHost", {
            "id": "request_id"
        })

        assert server.access_token == "my_token"
        assert server.host_id == 1
        assert server.host_name == "Test Host"

        assert server.request_id is None

        assert fakes_events.fired(AuthFlowEvents.HostMade).once()

        event: AuthFlowEvents.HostMade = fakes_events.fired(AuthFlowEvents.HostMade).event
        assert event.host.id == 1
        assert event.host.name == "Test Host"
