from unittest.mock import MagicMock, patch, call

from bumblebee.host.api.host_access import HostAccess
from bumblebee.host.api.host_refresh import HostRefresh
from bumblebee.host.api.make_host_request import MakeHostRequest
from bumblebee.host.api.show_host_request import ShowHostRequest
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.must_be_host_guard import MustBeHostGuard


class TestMustBeHostGuard(object):
    def test_host_refresh_is_called_if_access_token_exists(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["access_token"] = "my_token"

        host_refresh_mock = MagicMock(HostRefresh)
        resolver.instance(host_refresh_mock)

        def update_access_token():
            config["access_token"] = "my_new_token"

        host_refresh_mock.side_effect = update_access_token

        guard: MustBeHostGuard = resolver(MustBeHostGuard)

        guard()

        host_refresh_mock.assert_called_once()
        assert "access_token" in config
        assert config["access_token"] == "my_new_token"

    def test_host_request_flow(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        make_host_request_mock = MagicMock(MakeHostRequest)
        resolver.instance(make_host_request_mock)
        make_host_request_mock.return_value = None

        show_host_request_mock = MagicMock(ShowHostRequest)
        resolver.instance(show_host_request_mock)
        show_host_request_mock.side_effect = [
            {"status": "requested"},
            {"status": "claimed"}
        ]

        def add_host_info():
            config["access_token"] = "my_new_token"
            config["id"] = "my_host_id"
            config["name"] = "Test Host"

        host_access_mock = MagicMock(HostAccess)
        resolver.instance(host_access_mock)
        host_access_mock.side_effect = add_host_info

        guard: MustBeHostGuard = resolver(MustBeHostGuard)
        guard._loop_wait = 0

        guard()

        make_host_request_mock.assert_called_once()
        show_host_request_mock.assert_called()
        host_access_mock.assert_called_once()

        assert "access_token" in config
        assert config["access_token"] == "my_new_token"
        assert "id" in config
        assert config["id"] == "my_host_id"
        assert "name" in config
        assert config["name"] == "Test Host"
