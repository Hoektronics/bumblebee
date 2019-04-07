from unittest.mock import Mock, MagicMock, patch, call

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

            api.command.assert_called_once_with("UpdateAvailableConnections", [
                {
                    "type": "serial",
                    "port": "/dev/test-device"
                },
            ])

    def test_api_only_gets_called_once_if_nothing_has_changed_between_polling(self, resolver):
        api = Mock(BotQueueApi)
        resolver.instance(api)

        manager: AvailableConnectionsManager = resolver(AvailableConnectionsManager)

        with patch('bumblebee.host.managers.available_connections_manager.comports') as comports:
            port_info = MagicMock(ListPortInfo)
            port_info.device = "/dev/test-device"

            comports.return_value = [port_info]

            manager.poll()
            manager.poll()

            comports.assert_has_calls([call(), call()])

            api.command.assert_called_once_with("UpdateAvailableConnections", [
                {
                    "type": "serial",
                    "port": "/dev/test-device"
                },
            ])

    def test_changes_between_polling_calls_update(self, resolver):
        api = Mock(BotQueueApi)
        resolver.instance(api)

        manager: AvailableConnectionsManager = resolver(AvailableConnectionsManager)

        with patch('bumblebee.host.managers.available_connections_manager.comports') as comports:
            port_info_a = MagicMock(ListPortInfo)
            port_info_a.device = "/dev/test-device"
            port_info_b = MagicMock(ListPortInfo)
            port_info_b.device = "/dev/other-device"

            comports.side_effect = [
                [port_info_a],
                [port_info_a, port_info_b],
            ]

            manager.poll()
            manager.poll()

            comports.assert_has_calls([call(), call()])

            api.command.assert_has_calls([
                call("UpdateAvailableConnections", [
                    {
                        "type": "serial",
                        "port": "/dev/test-device"
                    },
                ]),
                call("UpdateAvailableConnections", [
                    {
                        "type": "serial",
                        "port": "/dev/test-device"
                    },
                    {
                        "type": "serial",
                        "port": "/dev/other-device"
                    }
                ]),
            ])
