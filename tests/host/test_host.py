from threading import Thread
from unittest.mock import Mock

from bumblebee.host import Host
from bumblebee.host.events import HostEvents
from bumblebee.host.managers.bots_manager import BotsManager
from bumblebee.host.managers.available_connections_manager import AvailableConnectionsManager


class TestHost(object):
    def test_host(self, resolver, fakes_events):
        fakes_events.fake(HostEvents.Startup)
        fakes_events.fake(HostEvents.Shutdown)

        bots_manager = Mock(BotsManager)
        bots_manager.start = Mock()
        resolver.instance(BotsManager, bots_manager)

        available_connections_manager = Mock(AvailableConnectionsManager)
        available_connections_manager.start = Mock()
        resolver.instance(AvailableConnectionsManager, available_connections_manager)

        host: Host = resolver(Host)
        thread = Thread(target=host.run, daemon=True)
        thread.start()

        bots_manager.start.assert_called_once()
        available_connections_manager.start.assert_called_once()

        assert fakes_events.fired(HostEvents.Startup).once()
        assert not fakes_events.fired(HostEvents.Shutdown)

        host.stop()
        thread.join()

        assert not thread.is_alive()

        assert fakes_events.fired(HostEvents.Startup).once()
        assert fakes_events.fired(HostEvents.Shutdown).once()