from unittest.mock import Mock, MagicMock, patch

from serial.tools.list_ports_common import ListPortInfo

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.framework.recurring_task import RecurringTask
from bumblebee.host.managers.available_connections_manager import AvailableConnectionsManager


class TestAvailableConnectionsManager(object):
    def test_scanning_is_done_as_a_recurring_task(self, resolver):
        resolver.instance(Mock(BotQueueApi))

        mock_polling_thread = MagicMock(RecurringTask)

        manager: AvailableConnectionsManager = resolver(AvailableConnectionsManager)
        manager._polling_thread = mock_polling_thread

        manager.start()

        mock_polling_thread.start.assert_called_once()

    def test_polling_searches_for_and_uploads_serial_ports(self, resolver):
        api = Mock(BotQueueApi)
        resolver.instance(api)

        manager: AvailableConnectionsManager = resolver(AvailableConnectionsManager)

        with patch('bumblebee.host.managers.available_connections_manager.comports') as comports:
            port_info = MagicMock(ListPortInfo)
            port_info.device = "/dev/test-device"

            comports.return_value = [port_info]

            manager.poll()

            comports.assert_called_once_with()

            api.command.assert_called_with("UpdateAvailableConnections", [
                {
                    "type": "serial",
                    "port": "/dev/test-device"
                }
            ])
