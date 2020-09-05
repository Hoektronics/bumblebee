from bumblebee.host.framework.logging import HostLogging
from deepdiff import DeepDiff
from serial.tools.list_ports import comports

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.framework.recurring_task import RecurringTask


class AvailableConnectionsManager(object):
    def __init__(self,
                 api: BotQueueApi,
                 host_logging: HostLogging):
        self.api = api
        self.host_logger = host_logging.get_logger("AvailableConnectionsManager")

        self._polling_thread = RecurringTask(5 * 60, self.poll)
        self._last_known_connections = {}

    def start(self):
        self._polling_thread.start()

    def poll(self):
        try:
            ports = comports()

            available_connections = list(map(lambda port_info: {
                "type": "serial",
                "port": port_info.device
            }, ports))

            diff = DeepDiff(self._last_known_connections, available_connections)

            if diff:
                self.api.command("UpdateAvailableConnections", available_connections)

            self._last_known_connections = available_connections
        except Exception as ex:
            self.host_logger.exception("Some exception occurred")
