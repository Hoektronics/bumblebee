from unittest.mock import MagicMock, Mock

from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.api.host_request import HostRequest
from bumblebee.host.configurations import HostConfiguration


class TestHostRequest(object):
    def test_host_request_sets_host_request_id(self, resolver):
        config = MagicMock(HostConfiguration)
        resolver.instance(HostConfiguration, config)

        config_data = {}

        config.__getitem__.side_effect = config_data.__getitem__
        config.__contains__.side_effect = config_data.__contains__
        config.__setitem__.side_effect = config_data.__setitem__

        api = Mock(BotQueueApi)
        api.post.return_value = {
            "data": {
                "id": "request_id"
            }
        }
        resolver.instance(api)

        host_request = resolver(HostRequest)

        host_request()

        api.post.assert_called_with("/host/requests")

        assert "host_request_id" in config
        assert config["host_request_id"] == "request_id"
