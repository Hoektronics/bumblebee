from unittest.mock import MagicMock, Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.queries.get_host_request import GetHostRequest
from bumblebee.host.configurations import HostConfiguration


class TestGetHostRequest(object):
    def test_showing_host_request(self, resolver, dictionary_magic, fakes_events):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["host_request_id"] = "request_id"

        api = Mock(BotQueueApi)
        api.command.return_value = {
            "id": "request_id",
            "status": "request_status"
        }
        resolver.instance(api)

        show_host_request = resolver(GetHostRequest)

        request_data = show_host_request()

        api.command.assert_called_once_with("GetHostRequest", {
            "id": "request_id"
        })

        assert "id" in request_data
        assert request_data["id"] == "request_id"
        assert request_data["status"] == "request_status"

        assert "host_request_id" in config
