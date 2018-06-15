from time import sleep, time

from bumblebee.host.api import BotQueueAPI
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import HostEvents
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.events import BotEvents
from bumblebee.host.framework import resolver
from bumblebee.host.framework.events import EventManager


class Host(object):
    def __init__(self, app_dirs):
        resolver(EventManager).bind(self)

        self.app_dirs = app_dirs
        self.config = HostConfiguration(self.app_dirs)
        self.api = BotQueueAPI(self.config)

    def run(self):
        HostEvents.Startup().fire()

        self._must_be_authenticated()

        self._update_bot_loop()

        HostEvents.Shutdown().fire()

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

    def _update_bot_loop(self):
        last_bots_time = 0

        bots = dict()

        while True:
            if time() > last_bots_time + 10:
                last_bots_time = time()

                bots_response = self.api.get_bots()

                for bot in bots_response:
                    if bot['id'] not in bots:
                        bots[bot['id']] = bot
                        BotEvents.BotAdded(bot).fire()

                for bot_id in bots:
                    filtered_bots = filter(lambda x: x['id'] == bot_id, bots_response)
                    if len(filtered_bots) == 0:
                        BotEvents.BotRemoved(bots[bot_id]).fire()

            sleep(.5)
