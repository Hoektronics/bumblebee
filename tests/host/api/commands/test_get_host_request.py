from unittest.mock import Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.get_host_request import GetHostRequest
from bumblebee.host.api.server import Server


class TestGetHostRequest(object):
    def test_showing_host_request(self, resolver , fakes_events):
        server = resolver(Server, url="https://server/")
        resolver.instance(server)

        server.request_id = "request_id"

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

        assert server.request_id is not None
