from unittest.mock import MagicMock, PropertyMock

from requests import Response

from bumblebee.host.api.rest import RestApi
from bumblebee.host.api.commands.make_host_request import MakeHostRequest
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents


class TestMakeHostRequest(object):
    def test_host_request_sets_host_request_id(self, resolver, dictionary_magic, fakes_events):
        fakes_events.fake(AuthFlowEvents.HostRequestMade)

        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "data": {
                "id": "request_id"
            }
        }

        api = MagicMock(RestApi)
        api.post.return_value = response
        resolver.instance(api)

        make_host_request = resolver(MakeHostRequest)

        make_host_request()

        api.post.assert_called_with("/host/requests")

        ok_mock.assert_called()
        response.json.assert_called()

        assert "host_request_id" in config
        assert config["host_request_id"] == "request_id"
        assert fakes_events.fired(AuthFlowEvents.HostRequestMade)
