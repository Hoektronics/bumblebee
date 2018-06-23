from unittest.mock import MagicMock, PropertyMock

import pytest
from requests import Response

from bumblebee.host.api.botqueue import BotQueueApi
from bumblebee.host.api.host_refresh import HostRefresh, AccessTokenNotFound
from bumblebee.host.configurations import HostConfiguration


class TestHostRefresh(object):
    def test_host_cannot_be_refreshed_if_no_access_token_is_available(self, resolver):
        config = MagicMock(HostConfiguration)
        resolver.instance(config)

        host_refresh = resolver(HostRefresh)

        with pytest.raises(AccessTokenNotFound):
            host_refresh()

    def test_host_calls_refresh_endpoint_with_token(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["access_token"] = "fake_access_token"

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "access_token": "my_new_token"
        }

        api = MagicMock(BotQueueApi)
        api.with_token.return_value = api
        api.post.return_value = response
        resolver.instance(api)

        host_refresh = resolver(HostRefresh)

        host_refresh()

        ok_mock.assert_called()
        response.json.assert_called()

        api.with_token.assert_called_once()
        api.post.assert_called_with("/host/refresh")

        assert "access_token" in config
        assert config["access_token"] == "my_new_token"
