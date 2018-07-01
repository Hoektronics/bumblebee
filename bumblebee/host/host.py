from time import sleep, time

from bumblebee.host.events import BotEvents
from bumblebee.host.events import HostEvents
from bumblebee.host.framework.events import bind_events
from bumblebee.host.framework.ioc import Resolver
from bumblebee.host.must_be_host_guard import MustBeHostGuard


@bind_events
class Host(object):
    def run(self):
        HostEvents.Startup().fire()

        # self._update_bot_loop()

        HostEvents.Shutdown().fire()

    # def _update_bot_loop(self):
    #     last_bots_time = 0
    #
    #     bots = dict()
    #
    #     while True:
    #         if time() > last_bots_time + 10:
    #             last_bots_time = time()
    #
    #             bots_response = self.api.get_bots()
    #
    #             for bot in bots_response:
    #                 if bot['id'] not in bots:
    #                     bots[bot['id']] = bot
    #                     BotEvents.BotAdded(bot).fire()
    #
    #             for bot_id in bots:
    #                 filtered_bots = filter(lambda x: x['id'] == bot_id, bots_response)
    #                 if len(filtered_bots) == 0:
    #                     BotEvents.BotRemoved(bots[bot_id]).fire()
    #
    #         sleep(.5)
