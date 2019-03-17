from unittest.mock import MagicMock, Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.refresh_access_token import RefreshAccessToken
from bumblebee.host.configurations import HostConfiguration


class TestRefreshAccessToken(object):
    def test_host_calls_refresh_endpoint_with_token(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["access_token"] = "fake_access_token"

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

        assert "access_token" in config
        assert config["access_token"] == "my_new_token"
