from unittest.mock import MagicMock, PropertyMock
from requests import Response

from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.api.host_access import HostAccess
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents


class TestHostAccess(object):
    def test_accepting_host_request(self, resolver, dictionary_magic, fakes_events):
        fakes_events.fake(AuthFlowEvents.HostMade)

        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["host_request_id"] = "request_id"

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "data": {
                "access_token": "my_token",
                "host": {
                    "id": 1,
                    "name": "Test Host"
                }
            }
        }

        api = MagicMock(BotQueueApi)
        api.post.return_value = response
        resolver.instance(api)

        host_access = resolver(HostAccess)

        host_access()

        api.post.assert_called_with("/host/requests/request_id/access")

        ok_mock.assert_called()
        response.json.assert_called()

        assert "access_token" in config
        assert config["access_token"] == "my_token"
        assert config["id"] == 1
        assert config["name"] == "Test Host"

        assert "host_request_id" not in config

        assert fakes_events.fired(AuthFlowEvents.HostMade)
