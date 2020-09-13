import pytest
import zeroconf

from bumblebee.host.events import ServerDiscovery
from bumblebee.host.managers.server_discovery_manager import ServerDiscoveryManager


class FakeServiceInfo(object):
    def __init__(self, server, port, properties=None):
        self.server = server
        self.port = port
        if properties is None:
            self.properties = {}
        else:
            self.properties = properties


@pytest.fixture
def mock_zeroconf(monkeypatch):
    class FakeZeroconf(object):
        def __init__(self):
            self._infos = []

        def add_info(self, type_, name, info: FakeServiceInfo):
            self._infos.append((type_, name, info))

        def get_service_info(self, type_, name):
            for info in self._infos:
                if info[0] == type_ and info[1] == name:
                    return info[2]

            return None

    fake = FakeZeroconf()

    monkeypatch.setattr(zeroconf, "Zeroconf", lambda: fake)

    return fake


@pytest.fixture
def mock_service_browser(monkeypatch):
    class FakeServiceBrowser(object):
        def __init__(self):
            self.zeroconf = None
            self.type = None
            self.handler = None
            self.cancel_called = False

        def cancel(self):
            self.cancel_called = True

    fake = FakeServiceBrowser()

    def fake_init(zc, type_, handler):
        fake.zeroconf = zc
        fake.type = type_
        fake.handler = handler

        return fake

    monkeypatch.setattr(zeroconf, "ServiceBrowser", fake_init)

    return fake


class TestServerDiscoveryManager(object):
    test_type = '_http._tcp.'
    test_domain = 'local.'
    test_name = 'example_name'

    def test_starting_server_discovery_sets_up_zeroconf(self, resolver, mock_zeroconf, mock_service_browser):
        server_discovery_manager: ServerDiscoveryManager = resolver(ServerDiscoveryManager)
        server_discovery_manager.start()

        assert mock_service_browser.zeroconf is mock_zeroconf
        assert mock_service_browser.type == f"{self.test_type}{self.test_domain}"
        assert mock_service_browser.handler is server_discovery_manager

    def test_stopping_server_discovery_stops_zeroconf(self, resolver, mock_zeroconf, mock_service_browser):
        server_discovery_manager: ServerDiscoveryManager = resolver(ServerDiscoveryManager)
        server_discovery_manager.start()
        server_discovery_manager.stop()

        assert mock_service_browser.cancel_called

    def test_stopping_server_discovery_does_not_stop_zeroconf_if_it_was_not_started(self,
                                                                                    resolver,
                                                                                    mock_zeroconf,
                                                                                    mock_service_browser):
        server_discovery_manager: ServerDiscoveryManager = resolver(ServerDiscoveryManager)
        server_discovery_manager.stop()

        assert not mock_service_browser.cancel_called

    def test_add_service_ignores_server_if_botqueue_property_is_not_set(self, resolver, mock_zeroconf, fakes_events):
        fakes_events.fake(ServerDiscovery.ServerDiscovered)

        server_discovery_manager: ServerDiscoveryManager = resolver(ServerDiscoveryManager)

        info = FakeServiceInfo('example.test.', 80)
        mock_zeroconf.add_info(self.test_type, self.test_name, info)

        server_discovery_manager.add_service(mock_zeroconf, self.test_type, self.test_name)

        assert not fakes_events.fired(ServerDiscovery.ServerDiscovered)

    def test_add_service_emits_server_if_botqueue_string_property_is_set(self, resolver, mock_zeroconf, fakes_events):
        fakes_events.fake(ServerDiscovery.ServerDiscovered)

        server_discovery_manager: ServerDiscoveryManager = resolver(ServerDiscoveryManager)

        info = FakeServiceInfo('example.test.', 80, {'botqueue': 1})
        mock_zeroconf.add_info(self.test_type, self.test_name, info)

        server_discovery_manager.add_service(mock_zeroconf, self.test_type, self.test_name)

        event_assertion = fakes_events.fired(ServerDiscovery.ServerDiscovered)
        assert event_assertion.once()
        assert event_assertion.event.url == "http://example.test"

    def test_add_service_emits_server_if_botqueue_bytes_property_is_set(self, resolver, mock_zeroconf, fakes_events):
        fakes_events.fake(ServerDiscovery.ServerDiscovered)

        server_discovery_manager: ServerDiscoveryManager = resolver(ServerDiscoveryManager)

        info = FakeServiceInfo('example.test.', 80, {b'botqueue': 1})
        mock_zeroconf.add_info(self.test_type, self.test_name, info)

        server_discovery_manager.add_service(mock_zeroconf, self.test_type, self.test_name)

        event_assertion = fakes_events.fired(ServerDiscovery.ServerDiscovered)
        assert event_assertion.once()
        assert event_assertion.event.url == "http://example.test"

    def test_add_service_emits_https_server_for_port_443(self, resolver, mock_zeroconf, fakes_events):
        fakes_events.fake(ServerDiscovery.ServerDiscovered)

        server_discovery_manager: ServerDiscoveryManager = resolver(ServerDiscoveryManager)

        info = FakeServiceInfo('example.test.', 443, {b'botqueue': 1})
        mock_zeroconf.add_info(self.test_type, self.test_name, info)

        server_discovery_manager.add_service(mock_zeroconf, self.test_type, self.test_name)

        event_assertion = fakes_events.fired(ServerDiscovery.ServerDiscovered)
        assert event_assertion.once()
        assert event_assertion.event.url == "https://example.test"

    def test_add_service_emits_server_without_trailing_dot_in_server(self, resolver, mock_zeroconf, fakes_events):
        fakes_events.fake(ServerDiscovery.ServerDiscovered)

        server_discovery_manager: ServerDiscoveryManager = resolver(ServerDiscoveryManager)

        info = FakeServiceInfo('example.test', 80, {b'botqueue': 1})
        mock_zeroconf.add_info(self.test_type, self.test_name, info)

        server_discovery_manager.add_service(mock_zeroconf, self.test_type, self.test_name)

        event_assertion = fakes_events.fired(ServerDiscovery.ServerDiscovered)
        assert event_assertion.once()
        assert event_assertion.event.url == "http://example.test"
