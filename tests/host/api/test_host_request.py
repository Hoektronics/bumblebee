from unittest.mock import MagicMock, PropertyMock

from requests import Response

from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.api.host_request import HostRequest
from bumblebee.host.configurations import HostConfiguration


class TestHostRequest(object):
    def test_host_request_sets_host_request_id(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(HostConfiguration, config)

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "data": {
                "id": "request_id"
            }
        }

        api = MagicMock(BotQueueApi)
        api.post.return_value = response
        resolver.instance(api)

        host_request = resolver(HostRequest)

        host_request()

        api.post.assert_called_with("/host/requests")

        ok_mock.assert_called()
        response.json.assert_called()

        assert "host_request_id" in config
        assert config["host_request_id"] == "request_id"
