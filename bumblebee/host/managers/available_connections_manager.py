from serial.tools.list_ports import comports

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.framework.recurring_task import RecurringTask


class AvailableConnectionsManager(object):
    def __init__(self,
                 api: BotQueueApi):
        self.api = api

        self._polling_thread = RecurringTask(5 * 60, self.poll)

    def start(self):
        self._polling_thread.start()

    def poll(self):
        ports = comports()

        available_connections = map(lambda port_info: {
            "type": "serial",
            "port": port_info.device
        }, ports)

        self.api.command("UpdateAvailableConnections", list(available_connections))
