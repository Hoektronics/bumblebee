from unittest.mock import MagicMock

from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.api.host_access import HostAccess
from bumblebee.host.configurations import HostConfiguration


class TestHostAccess(object):
    def test_accepting_host_request(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(HostConfiguration, config)

        config["host_request_id"] = "request_id"

        api = MagicMock(BotQueueApi)
        api.post.return_value = {
            "access_token": "my_token"
        }
        resolver.instance(api)

        host_access = resolver(HostAccess)

        host_access()

        api.post.assert_called_with("/host/requests/request_id/access")

        assert "access_token" in config
        assert config["access_token"] == "my_token"
        assert "host_request_id" not in config
