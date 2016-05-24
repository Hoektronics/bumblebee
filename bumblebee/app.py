import logging
import sys
import time

from bumblebee import bee_config
from bumblebee import botqueueapi
from bumblebee import hive
from bumblebee import stacktracer
from bumblebee import workerbee
from bumblebee import camera_control
from bumblebee.DeviceScanner import DeviceScanner
from bumblebee.RepeatedTimer import RepeatedTimer


class BumbleBee:
    sleepTime = 0.5

    def __init__(self):
        self.canUpgrade = False
        self.restart = False
        hive.loadLogger()
        self.log = logging.getLogger('botqueue')
        self.workers = {}
        self.config = bee_config.BeeConfig()
        self.lastScanData = None
        self.lastImageTime = time.time()
        self.quit = False

        # load up our api
        self.api = botqueueapi.BotQueueAPI(self.config)

        # this is our threading tracker
        stacktracer.trace_start("trace.html", interval=5, auto=True)  # Set auto flag to always update file!

    def main(self):
        # load up our bots and start processing them.
        self.log.info("BumbleBee Starting")

        deviceScanner = DeviceScanner()
        updateBotsTimer = RepeatedTimer(10, self.get_bots)

        camera_control.start()

        while not self.quit:
            time.sleep(self.sleepTime)

    def update_bots(self):
                self.get_bots()
                if not self.bots_are_busy() and self.canUpgrade:
                    self.log.debug("Bots aren't busy, we can restart")
                    self.restart = True
                    self.handle_quit()

    def get_bots(self):
        bot_api_result = self.api.getMyBots()

        # did we get a valid response?
        if bot_api_result is None:
            return

        if bot_api_result['status'] == 'success':
            # our list of bots this round
            bots_seen = []

            # loop over each bot and load or update its info
            for bot_data in bot_api_result['data']:
                # mark this one as seen.
                bots_seen.append(bot_data['id'])

                # do we already have this bot?
                if bot_data['id'] in self.workers:
                    worker = self.workers[bot_data['id']]
                    worker.update(bot_data)
                else:
                    self.log.info("Creating worker thread for bot %s" % bot_data['name'])
                    worker = workerbee.WorkerBee(self.api, bot_data)

                    self.workers[bot_data['id']] = worker

            # check to see if any of our current bots has dropped off the list
            for bot_id in self.workers.keys():
                # if we didn't find it, shut it down and remove the worker.
                if bot_id not in bots_seen:
                    worker = self.workers[bot_id]
                    self.log.info("Bot %s no longer found, shutting it down." % worker.bot_name)
                    worker.shutdown()
                    del self.workers[bot_id]

        else:
            self.log.error("Bot list failure: %s" % bot_api_result['error'])

    def bots_are_busy(self):
        bots_busy = False
        for worker in self.workers.values():
            bot = worker.bot
            if bot['status'] != 'idle' and bot['status'] != 'offline' and bot['status'] != 'error':
                bots_busy = True
        return bots_busy

    def handle_quit(self):
        self.quit = True
        self.log.info("Shutting down.")

        # tell all our threads to stop
        for worker in self.workers.values():
            worker.shutdown()

        # wait for all our threads to stop
        all_threads_dead = False
        while not all_threads_dead:
            all_threads_dead = True
            for worker in self.workers.values():
                if worker.is_alive():
                    all_threads_dead = False

        # stop our thread tracking.
        stacktracer.trace_stop()


def main():
    bee = BumbleBee()
    bee.main()


if __name__ == "__main__":
    sys.exit(main())
