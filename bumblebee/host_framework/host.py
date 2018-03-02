from time import sleep

from .api import BotQueueAPI
from .configuration import HostConfiguration
from .events.event import event_manager
from .events import HostEvents
from .events import AuthFlowEvents


class Host(object):
    def __init__(self, app_dirs):
        self.app_dirs = app_dirs
        self.config = HostConfiguration(self.app_dirs)
        self.api = BotQueueAPI(self.config)
        self.event_manager = event_manager

    def run(self):
        self.event_manager.fire(HostEvents.Startup)

        self._must_be_authenticated()

        self.event_manager.fire(HostEvents.Shutdown)

    def _must_be_authenticated(self):
        if self.api.is_access_valid():
            return

        host_request = self.api.host_request()

        AuthFlowEvents.HostRequestMade(host_request).fire()

        while True:
            host_request = self.api.request_status(host_request['id'])

            if host_request['status'] == 'claimed':
                host_data = self.api.get_host(host_request['id'])

                self.config['host'] = {
                    'access_token': host_data['access_token'],
                    'id': host_data['host']['id'],
                    'name': host_data['host']['name'],
                }
                if "host_request_id" in self.config:
                    del self.config["host_request_id"]

                self.config.save()

                AuthFlowEvents.HostMade(host_data['host']).fire()

                self.api.update_auth()
                break

            sleep(10)
