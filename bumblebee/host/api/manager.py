from bumblebee.host import on
from bumblebee.host.api.socket import WebSocketApi
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.framework.events import bind_events


@bind_events
class ApiManager(object):
    def __init__(self,
                 config: HostConfiguration,
                 socket: WebSocketApi):
        self.config = config
        self.socket = socket

        self.handlers = []
        self.tasks = []
        self._start_called = False

        if "id" in self.config:
            host_id = self.config["id"]
            self._subscribe_to_host_channel(host_id)

    @on(AuthFlowEvents.HostMade)
    def _subscribe_to_host(self, event: AuthFlowEvents.HostMade):
        host_id = event.host.id
        self._subscribe_to_host_channel(host_id)

    def _subscribe_to_host_channel(self, host_id):
        self.socket.subscribe(f"private-host.{host_id}")

    def add_handler(self, handler):
        self.handlers.append(handler)

        if hasattr(handler, 'tasks'):
            handler_tasks = handler.tasks()
            self.tasks.extend(handler_tasks)

            if self._start_called:
                for task in handler_tasks:
                    task.start()

    def start(self):
        for task in self.tasks:
            task.start()
        self._start_called = True
