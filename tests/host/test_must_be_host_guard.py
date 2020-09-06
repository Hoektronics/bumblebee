from unittest.mock import MagicMock, call

from bumblebee.host.api.commands.convert_request_to_host import ConvertRequestToHost
from bumblebee.host.api.commands.refresh_access_token import RefreshAccessToken
from bumblebee.host.api.commands.create_host_request import CreateHostRequest
from bumblebee.host.api.commands.get_host_request import GetHostRequest
from bumblebee.host.api.server import Server
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import ServerDiscovery
from bumblebee.host.must_be_host_guard import MustBeHostGuard


class TestMustBeHostGuard(object):
    def test_host_refresh_is_called_if_access_token_exists(self, resolver):
        # config = dictionary_magic(MagicMock(HostConfiguration))
        # resolver.instance(config)
        config = resolver(HostConfiguration)

        server_url = "https://example.test"
        config["server"] = server_url
        config["servers"] = {
            server_url: {
                "access_token": "my_token"
            }
        }

        host_refresh_mock = MagicMock(RefreshAccessToken)
        resolver.instance(RefreshAccessToken, host_refresh_mock)

        def update_access_token():
            server_config = config["servers"][server_url]
            server_config["access_token"] = "my_new_token"

        host_refresh_mock.side_effect = update_access_token

        guard: MustBeHostGuard = resolver(MustBeHostGuard)

        guard()

        host_refresh_mock.assert_called_once()
        assert "access_token" in config["servers"][server_url]
        assert config["servers"][server_url]["access_token"] == "my_new_token"

        server = resolver(Server)
        assert server.url == server_url
        assert "server" in config
        assert config["server"] == server.url

    def test_server_discovery_creates_host_request(self, resolver):
        _mocks = {}
        foo_url = "http://foo.test"
        bar_url = "http://bar.test"

        def _creat_host_request_bind(*args):
            server = args[0]
            if server.url not in _mocks:
                _mocks[server.url] = MagicMock(CreateHostRequest)
            return _mocks[server.url]

        resolver.bind(CreateHostRequest, _creat_host_request_bind)

        # Bind events
        resolver(MustBeHostGuard)

        ServerDiscovery.ServerDiscovered(foo_url).fire()

        assert foo_url in _mocks
        assert bar_url not in _mocks

    def test_guard_checks_all_known_host_requests(self, resolver):
        config = resolver(HostConfiguration)

        foo_url = "http://foo.test"
        bar_url = "http://bar.test"

        config["servers"] = {
            foo_url: {"request_id": "abcdabcd"},
            bar_url: {"request_id": "deadbeef"},
        }

        _get_host_request_mocks = {}

        def _get_host_request_bind(*args):
            binding_server = args[0]
            if binding_server.url not in _get_host_request_mocks:
                get_host_request = MagicMock(GetHostRequest)
                _get_host_request_mocks[binding_server.url] = get_host_request

                if binding_server.url == foo_url:
                    get_host_request.side_effect = [
                        {"status": "requested"},
                        {"status": "claimed"}
                    ]
                else:
                    get_host_request.return_value = {"status": "requested"}

            return _get_host_request_mocks[binding_server.url]

        resolver.bind(GetHostRequest, _get_host_request_bind)

        _convert_request_to_host_mocks = {}

        def _convert_request_to_host_bind(*args):
            binding_server = args[0]
            if binding_server.url not in _convert_request_to_host_mocks:
                _convert_request_to_host_mocks[binding_server.url] = MagicMock(ConvertRequestToHost)
            return _convert_request_to_host_mocks[binding_server.url]

        resolver.bind(ConvertRequestToHost, _convert_request_to_host_bind)

        guard: MustBeHostGuard = resolver(MustBeHostGuard)
        guard._loop_wait = 0

        guard()

        assert _get_host_request_mocks[foo_url].call_count == 2
        assert _convert_request_to_host_mocks[foo_url] is not None
        _convert_request_to_host_mocks[foo_url].assert_called_once()

        assert _get_host_request_mocks[bar_url].call_count == 1
        assert bar_url not in _convert_request_to_host_mocks

        server = resolver(Server)
        assert server.url == foo_url
        assert "server" in config
        assert config["server"] == server.url
