from unittest.mock import Mock, MagicMock

import pytest

from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.api.host_refresh import HostRefresh, AccessTokenNotFound
from bumblebee.host.configurations import HostConfiguration


class TestHostRefresh(object):
    def test_host_cannot_be_refreshed_if_no_access_token_is_available(self, resolver):
        config = MagicMock(HostConfiguration)
        resolver.instance(HostConfiguration, config)

        host_refresh = resolver(HostRefresh)

        with pytest.raises(AccessTokenNotFound):
            host_refresh()

    def test_host_calls_refresh_endpoint_with_token(self, resolver):
        config = MagicMock(HostConfiguration)
        resolver.instance(HostConfiguration, config)

        config_data = {
            "access_token": "fake_access_token"
        }

        config.__getitem__.side_effect = config_data.__getitem__
        config.__contains__.side_effect = config_data.__contains__
        config.__setitem__.side_effect = config_data.__setitem__

        api = Mock(BotQueueApi)
        api.with_token.return_value = api
        api.post.return_value = {
            "access_token": "my_new_token"
        }
        resolver.instance(api)

        host_refresh = resolver(HostRefresh)

        host_refresh()

        api.with_token.assert_called_once()
        api.post.assert_called_with("/host/refresh")

        assert "access_token" in config
        assert config["access_token"] == "my_new_token"
