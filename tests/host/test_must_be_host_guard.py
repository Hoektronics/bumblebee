from unittest.mock import MagicMock, call

from bumblebee.host.api.commands.convert_request_to_host import ConvertRequestToHost
from bumblebee.host.api.commands.refresh_access_token import RefreshAccessToken
from bumblebee.host.api.commands.create_host_request import CreateHostRequest
from bumblebee.host.api.commands.get_host_request import GetHostRequest
from bumblebee.host.api.server import Server
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import ServerDiscovery
from bumblebee.host.managers.server_discovery_manager import ServerDiscoveryManager
from bumblebee.host.must_be_host_guard import MustBeHostGuard


class TestMustBeHostGuard(object):
    def test_host_refresh_is_called_if_access_token_exists(self, resolver):
        config = resolver(HostConfiguration)
        server_discovery_manager = MagicMock(ServerDiscoveryManager)
        resolver.instance(ServerDiscoveryManager, server_discovery_manager)

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

        server_discovery_manager.start.assert_not_called()
        server_discovery_manager.stop.assert_not_called()

    def test_server_discovery_creates_host_request(self, resolver):
        server_discovery_manager = MagicMock(ServerDiscoveryManager)
        resolver.instance(ServerDiscoveryManager, server_discovery_manager)

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

        server_discovery_manager.start.assert_not_called()
        server_discovery_manager.stop.assert_not_called()

    def test_server_discovery_creates_host_request_when_needed(self, resolver):
        server_discovery_manager = MagicMock(ServerDiscoveryManager)
        resolver.instance(ServerDiscoveryManager, server_discovery_manager)

        _mocks = {}
        foo_url = "http://foo.test"
        bar_url = "http://bar.test"
        resolver(Server, url=bar_url).request_id = "deadbeef"

        def _creat_host_request_bind(*args):
            server = args[0]
            if server.url not in _mocks:
                _mocks[server.url] = MagicMock(CreateHostRequest)
            return _mocks[server.url]

        resolver.bind(CreateHostRequest, _creat_host_request_bind)

        # Bind events
        resolver(MustBeHostGuard)

        ServerDiscovery.ServerDiscovered(foo_url).fire()
        ServerDiscovery.ServerDiscovered(bar_url).fire()

        assert foo_url in _mocks
        assert bar_url not in _mocks

        server_discovery_manager.start.assert_not_called()
        server_discovery_manager.stop.assert_not_called()

    def test_guard_checks_all_known_host_requests(self, resolver):
        config = resolver(HostConfiguration)
        server_discovery_manager = MagicMock(ServerDiscoveryManager)
        resolver.instance(ServerDiscoveryManager, server_discovery_manager)

        foo_url = "http://foo.test"
        bar_url = "http://bar.test"
        baz_url = "http://baz.test"

        config["servers"] = {
            foo_url: {"request_id": "abcdabcd"},
            bar_url: {"request_id": "deadbeef"},
            baz_url: {},
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

        assert baz_url not in _get_host_request_mocks
        assert baz_url not in _convert_request_to_host_mocks

        server = resolver(Server)
        assert server.url == foo_url
        assert "server" in config
        assert config["server"] == server.url

        server_discovery_manager.start.assert_called_once()
        server_discovery_manager.stop.assert_called_once()

    def test_guard_reissues_expired_host_requests(self, resolver):
        config = resolver(HostConfiguration)
        server_discovery_manager = MagicMock(ServerDiscoveryManager)
        resolver.instance(ServerDiscoveryManager, server_discovery_manager)

        url = "http://foo.test"
        server = resolver(Server, url=url)
        server.request_id = "abcdabcd"

        get_host_request_mock = MagicMock(GetHostRequest)

        called_for_first_id = False
        called_for_second_id = False

        def _get_host_request_side_effect():
            nonlocal called_for_first_id
            nonlocal called_for_second_id
            if server.request_id == "abcdabcd":
                called_for_first_id = True
                return {"status": "expired"}
            elif server.request_id == "deadbeef":
                called_for_second_id = True
                return {"status": "claimed"}
            else:
                raise ValueError("Unexpected request id")

        get_host_request_mock.side_effect = _get_host_request_side_effect
        resolver.instance(GetHostRequest, get_host_request_mock)

        convert_request_mock = MagicMock(ConvertRequestToHost)

        def _convert_request_side_effect():
            del server.request_id

        convert_request_mock.side_effect = _convert_request_side_effect
        resolver.instance(ConvertRequestToHost, convert_request_mock)

        create_host_request_mock = MagicMock(CreateHostRequest)

        def _create_host_request_side_effect():
            server.request_id = "deadbeef"

        create_host_request_mock.side_effect = _create_host_request_side_effect
        resolver.instance(CreateHostRequest, create_host_request_mock)

        guard: MustBeHostGuard = resolver(MustBeHostGuard)
        guard._loop_wait = 0

        guard()

        server_discovery_manager.start.assert_called_once()
        server_discovery_manager.stop.assert_called_once()

        assert get_host_request_mock.call_count == 2
        convert_request_mock.assert_called_once()
        create_host_request_mock.assert_called_once()

        assert called_for_first_id
        assert called_for_second_id

        server = resolver(Server)
        assert server.url == url
        assert server.request_id is None
