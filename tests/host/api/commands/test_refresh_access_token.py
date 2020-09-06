from unittest.mock import MagicMock, Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.refresh_access_token import RefreshAccessToken
from bumblebee.host.api.server import Server


class TestRefreshAccessToken(object):
    def test_host_calls_refresh_endpoint_with_token(self, resolver):
        server = resolver(Server, url="https://server/")
        resolver.instance(server)
        server.access_token = "fake_access_token"

        api = Mock(BotQueueApi)
        api.command.return_value = {
            "access_token": "my_new_token",
            "host": {
                "id": 1,
                "name": "Test Host"
            }
        }
        resolver.instance(api)

        host_refresh = resolver(RefreshAccessToken)

        host_refresh()

        api.command.assert_called_once_with("RefreshAccessToken")

        assert server.access_token == "my_new_token"
