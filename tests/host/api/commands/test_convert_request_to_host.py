from unittest.mock import MagicMock, Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.convert_request_to_host import ConvertRequestToHost
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents


class TestConvertRequestToHost(object):
    def test_accepting_host_request(self, resolver, dictionary_magic, fakes_events):
        fakes_events.fake(AuthFlowEvents.HostMade)

        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["host_request_id"] = "request_id"

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

        assert "access_token" in config
        assert config["access_token"] == "my_token"
        assert config["id"] == 1
        assert config["name"] == "Test Host"

        assert "host_request_id" not in config

        assert fakes_events.fired(AuthFlowEvents.HostMade).once()

        event: AuthFlowEvents.HostMade = fakes_events.fired(AuthFlowEvents.HostMade).event
        assert event.host.id == 1
        assert event.host.name == "Test Host"
