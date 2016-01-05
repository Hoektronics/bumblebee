import Queue
import curses
import hashlib
import json
import logging
import sys
import threading
import time

from bumblebee import botqueueapi
from bumblebee import camera_control
from bumblebee import hive
from bumblebee import stacktracer
from bumblebee import workerbee
from bumblebee import bee_config

try:
    from bumblebee import autoupgrade

    auto_update = True
except ImportError:
    auto_update = False
    pass


class BumbleBee:
    sleepTime = 0.5

    def __init__(self):
        if auto_update:
            self.app = autoupgrade.AutoUpgrade("bqclient", "https://pypi.python.org/simple")
        else:
            self.app = None

        self.lastScanUpdate = 0
        self.lastBotUpdate = 0
        self.lastUpgradeCheck = 0
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
        self.log.info("Started up, loading bot list.")

        while not self.quit:
            # any messages?
            self.check_messages()
            if time.time() - self.lastBotUpdate > 10:
                self.get_bots()
                if not self.bots_are_busy() and self.canUpgrade:
                    self.log.debug("Bots aren't busy, we can restart")
                    self.restart = True
                    self.handle_quit()
                self.lastBotUpdate = time.time()
            if time.time() - self.lastScanUpdate > 60:
                self.scan_devices()
                self.lastScanUpdate = time.time()
            if time.time() - self.lastUpgradeCheck > 120:
                self.canUpgrade = self.app is not None and self.app.check()
                self.lastUpgradeCheck = time.time()

            time.sleep(self.sleepTime)

        if self.canUpgrade:
            self.upgrade()

    def load_bot(self, mosi_queue, miso_queue, data):
        try:
            self.log.info("Loading bot %s" % data['name'])
            worker = workerbee.WorkerBee(data, mosi_queue, miso_queue)
            worker.run()
        except KeyboardInterrupt:
            self.log.debug("Bot %s exiting from keyboard interrupt." % data['name'])
        except Exception as ex:
            self.log.exception(ex)

    def scan_devices(self):
        # look up our data
        data = {
            'bots': hive.scanBots(),
            'cameras': camera_control.scanCameras()
        }

        scan_data = json.dumps(data)
        if scan_data != self.lastScanData or (self.lastImageTime + 60 < time.time()):
            self.lastScanData = scan_data

            camera_files = []
            if len(data['cameras']):
                for idx, camera in enumerate(data['cameras']):
                    outfile = camera['name'] + '.jpg'
                    try:
                        if camera_control.takePicture(camera['device'], watermark=None, output=outfile):
                            self.lastImageTime = time.time()
                            full_image_path = hive.getImageDirectory(outfile)
                            camera_files.append(full_image_path)
                    except Exception as ex:
                        self.log.exception(ex)

            # now update the main site
            self.api.sendDeviceScanResults(data, camera_files)

    def get_bots(self):

        self.scan_devices()

        bots = self.api.getMyBots()
        self.check_messages()  # must come after getMyBots

        # did we get a valid response?
        if bots:
            if bots['status'] == 'success':
                # our list of bots this round
                latest_bots = {}

                # loop over each bot and load or update its info
                for row in bots['data']:
                    # mark this one as seen.
                    latest_bots[row['id']] = True

                    # do we already have this bot?
                    if row['id'] in self.workers:
                        link = self.workers[row['id']]
                    else:
                        self.log.info("Creating worker thread for bot %s" % row['name'])
                        # create our thread and start it.
                        # master_in, slave_out = multiprocessing.Pipe()
                        # slave_in, master_out = multiprocessing.Pipe()
                        mosi_queue = Queue.Queue()
                        miso_queue = Queue.Queue()
                        p = threading.Thread(target=self.load_bot, args=(mosi_queue, miso_queue, row,))
                        p.name = "Bot-%s" % row['name']
                        p.daemon = True
                        p.start()

                        # make our link object to track all this cool stuff.
                        link = hive.Object()
                        link.bot = row
                        link.process = p
                        link.miso_queue = miso_queue
                        link.mosi_queue = mosi_queue
                        link.job = None
                        self.workers[row['id']] = link

                    # should we find a new job?
                    if link.bot['status'] == 'idle':
                        self.get_new_job(link)

                # check to see if any of our current bots has dropped off the list
                ids = self.workers.keys()
                for idx in ids:
                    # if we didnt find it, shut it down and remove the worker.
                    if idx not in latest_bots:
                        link = self.workers[idx]
                        self.log.info("Bot %s no longer found, shutting it down." % link.bot['name'])
                        self.send_message(link, 'shutdown')
                        del self.workers[idx]

            else:
                self.log.error("Bot list failure: %s" % bots['error'])

    def bots_are_busy(self):
        bots_busy = False
        for idx, link in self.workers.iteritems():
            bot = link.bot
            if bot['status'] != 'idle' and bot['status'] != 'offline' and bot['status'] != 'error':
                bots_busy = True
        return bots_busy

    def upgrade(self):
        if self.canUpgrade and self.restart:
            self.log.info("Updating...")
            self.app.upgrade(dependencies=True)
            self.log.info("Update complete. Restarting")
            self.app.restart()

    def handle_quit(self):
        self.quit = True
        self.log.info("Shutting down.")

        # tell all our threads to stop
        for idx, link in self.workers.iteritems():
            self.send_message(link, 'shutdown')

        # wait for all our threads to stop
        threads = len(self.workers)
        while threads > 0:
            for idx, link in self.workers.iteritems():
                threads = 0
                if link.process.is_alive():
                    threads += 1

        # stop our thread tracking.
        stacktracer.trace_stop()

    def send_message(self, link, name, data=False):
        self.check_messages()
        # self.log.debug("Mothership: sending message")
        message = workerbee.Message(name, data)
        link.mosi_queue.put(message)

    # loop through our workers and check them all for messages
    def check_messages(self):
        # self.log.debug("Mothership: Checking messages.")
        for idx, link in self.workers.iteritems():
            while not link.miso_queue.empty():
                message = link.miso_queue.get(False)
                self.handle_message(link, message)
                link.miso_queue.task_done()

    # these are the messages we know about.
    def handle_message(self, link, message):
        # self.log.debug("Mothership got message %s" % message.name)
        if message.name == 'job_update':
            link.job = message.data
        elif message.name == 'bot_update':
            if link.bot['status'] != message.data['status']:
                self.log.info("Mothership: %s status changed from %s to %s" % (
                    link.bot['name'], link.bot['status'], message.data['status']))
            link.bot = message.data

    def get_new_job(self, link):
        find_job_result = self.api.findNewJob(link.bot['id'], link.bot['driver_config']['can_slice'])
        if find_job_result['status'] == 'success':
            if len(find_job_result['data']):
                job = find_job_result['data']
                grab_job_result = self.api.grabJob(link.bot['id'], job['id'], link.bot['driver_config']['can_slice'])

                if grab_job_result['status'] == 'success':
                    # save it to our link.
                    link.job = job
                    link.bot['job'] = job

                    # notify the bot
                    self.send_message(link, 'updatedata', link.bot)

                    return True
        else:
            raise Exception("Error finding new job: %s" % find_job_result['error'])
        return False


def main():
    bee = BumbleBee()
    bee.main()


if __name__ == "__main__":
    sys.exit(main())
