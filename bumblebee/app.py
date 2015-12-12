import curses
import hashlib
import json
import logging
import os
import sys
import threading
import time
import Queue

from bumblebee import botqueueapi
from bumblebee import camera_control
from bumblebee import hive
from bumblebee import stacktracer
from bumblebee import workerbee

try:
    from bumblebee import autoupgrade
    auto_update = True
except ImportError:
    auto_update = False
    pass

# Redirect stderr to nothing
#sys.stderr = open(os.devnull, 'w')

class BumbleBee():
    sleepTime = 0.5

    def __init__(self):
        if auto_update:
            self.app = autoupgrade.AutoUpgrade("bqclient", "https://pypi.python.org/simple")
        else:
            self.app = None
        self.screen = None
        self.lastScanUpdate = 0
        self.lastScreenUpdate = 0
        self.lastBotUpdate = 0
        self.lastUpgradeCheck = 0
        self.canUpgrade = False
        self.restart = False
        hive.loadLogger()
        self.log = logging.getLogger('botqueue')
        self.workers = {}
        self.workerDataAge = {}
        self.config = hive.config.get()
        self.lastScanData = None
        self.lastImageTime = time.time()
        self.quit = False

        # check for default info.
        if 'app_url' not in self.config:
            self.config['app_url'] = "https://www.botqueue.com"
            hive.config.save(self.config)

        # create a unique hash that will identify this computers requests
        if 'uid' not in self.config or not self.config['uid']:
            self.config['uid'] = hashlib.sha1(str(time.time())).hexdigest()
            hive.config.save(self.config)

            # slicing options moved to driver config
        if 'can_slice' in self.config:
            del self.config['can_slice']
            hive.config.save(self.config)

            # load up our api
        self.api = botqueueapi.BotQueueAPI()

        # this is our threading tracker
        stacktracer.trace_start("trace.html", interval=5, auto=True)  # Set auto flag to always update file!

    def loadBot(self, mosi_queue, miso_queue, data):
        try:
            self.log.info("Loading bot %s" % data['name'])
            worker = workerbee.WorkerBee(data, mosi_queue, miso_queue)
            worker.run()
        except KeyboardInterrupt:
            self.log.debug("Bot %s exiting from keyboard interrupt." % data['name'])
        except Exception as ex:
            self.log.exception(ex)

    def scanDevices(self):

        # look up our data
        data = {}
        data['bots'] = hive.scanBots()
        data['cameras'] = camera_control.scanCameras()

        scanData = json.dumps(data)
        if scanData != self.lastScanData or (self.lastImageTime + 60 < time.time()):
            self.lastScanData = scanData

            camera_files = []
            if len(data['cameras']):
                for idx, camera in enumerate(data['cameras']):
                    outfile = camera['name'] + '.jpg'
                    try:
                        if camera_control.takePicture(camera['device'], watermark=None, output=outfile):
                            self.lastImageTime = time.time()
                            fullImgPath = hive.getImageDirectory(outfile)
                            camera_files.append(fullImgPath)
                    except Exception as ex:
                        self.log.exception(ex)

            # now update the main site
            self.api.sendDeviceScanResults(data, camera_files)

    def getBots(self):

        self.scanDevices()

        startTime = time.time()
        bots = self.api.getMyBots()
        self.checkMessages()  # must come after getMyBots

        # did we get a valid response?
        if bots:
            if (bots['status'] == 'success'):
                # our list of bots this round
                latestBots = {}

                # loop over each bot and load or update its info
                for row in bots['data']:
                    # mark this one as seen.
                    latestBots[row['id']] = True

                    # do we already have this bot?
                    if row['id'] in self.workers:
                        link = self.workers[row['id']]
                        if not (row['id'] in self.workerDataAge):
                            self.workerDataAge[row['id']] = 0
                        if self.workerDataAge[row['id']] < startTime:
                            self.sendMessage(link, 'updatedata', row)
                            link.bot = row
                            self.workerDataAge[row['id']] = startTime
                        else:
                            self.log.debug("Worker for %s is stale: %s / %s" % (
                                row['name'], startTime, self.workerDataAge[row['id']]))
                    else:
                        self.log.info("Creating worker thread for bot %s" % row['name'])
                        # create our thread and start it.
                        # master_in, slave_out = multiprocessing.Pipe()
                        # slave_in, master_out = multiprocessing.Pipe()
                        mosi_queue = Queue.Queue()
                        miso_queue = Queue.Queue()
                        p = threading.Thread(target=self.loadBot, args=(mosi_queue, miso_queue, row,))
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
                        self.getNewJob(link)

                # check to see if any of our current bots has dropped off the list
                ids = self.workers.keys()
                for idx in ids:
                    # if we didnt find it, shut it down and remove the worker.
                    if idx not in latestBots:
                        link = self.workers[idx]
                        self.log.info("Bot %s no longer found, shutting it down." % link.bot['name'])
                        self.sendMessage(link, 'shutdown')
                        del self.workers[idx]

            else:
                self.log.error("Bot list failure: %s" % bots['error'])

    def main(self):
        # load up our bots and start processing them.
        self.log.info("Started up, loading bot list.")

        if sys.stdout.isatty():
            curses.wrapper(self.mainMenu)
        else:
            while not self.quit:
                self.handleServerUpdates()
                time.sleep(self.sleepTime)
        if self.canUpgrade:
            self.upgrade()


    def handleServerUpdates(self):
        # any messages?
        self.checkMessages()
        if time.time() - self.lastBotUpdate > 10:
            self.getBots()
            if not self.botsAreBusy() and self.canUpgrade:
                self.log.debug("Bots aren't busy, we can restart")
                self.restart = True
                self.handleQuit()
            self.lastBotUpdate = time.time()
        if time.time() - self.lastScanUpdate > 60:
            self.scanDevices()
            self.lastScanUpdate = time.time()
        if time.time() - self.lastUpgradeCheck > 120:
            self.canUpgrade = self.app is not None and self.app.check()
            self.lastUpgradeCheck = time.time()

    def botsAreBusy(self):
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

    def mainMenu(self, screen):
        try:
            self.screen = screen
            self.screenSize = screen.getmaxyx()
            self.screen.nodelay(1)  # non-blocking, so we can refresh the screen

            # Try/except for the terminals that don't support hiding the cursor
            try:
                curses.curs_set(0)
            except:
                pass

            # show an intro screen.
            self.screen.erase()
            self.screen.addstr(
                "\nBotQueue v%s starting up. Scanning devices, please be patient.\n\n" % self.api.version)
            self.screen.refresh()

            # our main loop until we're done.
            while not self.quit:

                self.handleServerUpdates()

                if time.time() - self.lastScreenUpdate > 1:
                    self.drawMenu()
                    self.lastScreenUpdate = time.time()

                # keyboard interface stuff.
                key = self.screen.getch()
                if key >= 0:
                    if key == ord('q'):
                        self.handleQuit()

                time.sleep(self.sleepTime)
        except KeyboardInterrupt:
            self.handleQuit()

    def handleQuit(self):
        self.quit = True
        self.log.info("Shutting down.")

        # tell all our threads to stop
        for idx, link in self.workers.iteritems():
            self.sendMessage(link, 'shutdown')

        # wait for all our threads to stop
        threads = len(self.workers)
        self.lastUpdate = 0
        while threads > 0:
            for idx, link in self.workers.iteritems():
                threads = 0
                if link.process.is_alive():
                    threads = threads + 1
            if self.screen is not None and time.time() - self.lastUpdate > 1:
                self.screen.erase()
                self.screen.addstr("%s\n\n" % time.asctime())
                self.screen.addstr("Waiting for worker threads to shut down (%d/%d)" % (threads, len(self.workers)))
                self.screen.refresh()
                self.lastUpdate = time.time()

        # stop our thread tracking.
        stacktracer.trace_stop()

        if self.screen is not None:
            self.screen.erase()

    def sendMessage(self, link, name, data=False):
        self.checkMessages()
        # self.log.debug("Mothership: sending message")
        message = workerbee.Message(name, data)
        link.mosi_queue.put(message)

    # loop through our workers and check them all for messages
    def checkMessages(self):
        # self.log.debug("Mothership: Checking messages.")
        for idx, link in self.workers.iteritems():
            while not link.miso_queue.empty():
                message = link.miso_queue.get(False)
                self.handleMessage(link, message)
                link.miso_queue.task_done()

    # these are the messages we know about.
    def handleMessage(self, link, message):
        # self.log.debug("Mothership got message %s" % message.name)
        if message.name == 'job_update':
            link.job = message.data
        elif message.name == 'bot_update':
            if link.bot['status'] != message.data['status']:
                self.log.info("Mothership: %s status changed from %s to %s" % (
                    link.bot['name'], link.bot['status'], message.data['status']))
            link.bot = message.data
            self.workerDataAge[message.data['id']] = time.time()

    def drawMenu(self):
        # self.log.debug("drawing screen")

        try:
            self.screen.erase()
            self.screenSize = self.screen.getmaxyx()
            self.screen.addstr("BotQueue v%s\n" % (self.api.version))
            self.screen.addstr("Time: %s\n\n" % (time.asctime()))

            if len(self.workers):
                if self.screenSize[1] >= 72:
                    self.screen.addstr("%6s  %20s  %10s  %8s  %8s  %10s" % (
                        "ID", "BOT NAME", "STATUS", "PROGRESS", "JOB ID", "STATUS"))
                    if self.screenSize[1] > 72:
                        self.screen.addstr("\n")
                else:
                    self.screen.addstr("%10s  %8s  %8s  %7s" % ("BOT NAME", "STATUS", "PROGRESS", "STATUS"))
                    if self.screenSize[1] > 39:
                        self.screen.addstr("\n")
                for idx, link in self.workers.iteritems():
                    if self.screenSize[1] >= 72:
                        self.screen.addstr("%6s  %20s  %10s  " % (link.bot['id'], link.bot['name'], link.bot['status']))
                    else:
                        self.screen.addstr("%10s  %8s  " % (link.bot['name'], link.bot['status']))
                    if (link.bot['status'] == 'working'
                        or link.bot['status'] == 'waiting'
                        or link.bot['status'] == 'slicing')\
                            and link.job:
                        progress_string = "{num:{width}.2f}".format(num=float(link.job['progress']), width=6)
                        if self.screenSize[1] >= 72:
                            self.screen.addstr(
                                " %s%%  %8s  %10s" % (progress_string, link.job['id'], link.job['status']))
                        else:
                            self.screen.addstr(" %s%%  %7s" % (progress_string, link.job['status']))
                    elif link.bot['status'] == 'error':
                        self.screen.addstr("%s" % link.bot['error_text'])
                    else:
                        if self.screenSize[1] >= 72:
                            self.screen.addstr("   --         --          --")
                        else:
                            self.screen.addstr("   --        --")
                    self.screen.addstr("\n")
            else:
                self.screen.addstr("No bots found.  Add a bot on BotQueue.com and assign it to this app.\n")
            self.screen.addstr("\nq = quit program\n")

            # show our network status.
            self.screen.addstr("\nNetwork Status: ")
            if self.api.netStatus:
                self.screen.addstr("ONLINE")
            else:
                self.screen.addstr("OFFLINE")
            self.screen.addstr(" | Net Errors: %s" % self.api.netErrors)

            self.screen.refresh()
        except curses.error as ex:
            self.log.error("Problem drawing screen - too small? %s" % ex)

    def getNewJob(self, link):
        # self.log.info("Bot %s looking for new job." % link.bot['name'])

        result = self.api.findNewJob(link.bot['id'], link.bot['driver_config']['can_slice'])
        if (result['status'] == 'success'):
            if (len(result['data'])):
                job = result['data']
                startTime = time.time()
                jresult = self.api.grabJob(link.bot['id'], job['id'], link.bot['driver_config']['can_slice'])

                if (jresult['status'] == 'success'):
                    # save it to our link.
                    link.job = job
                    link.bot['job'] = job

                    # notify the bot
                    self.sendMessage(link, 'updatedata', link.bot)
                    self.workerDataAge[link.bot['id']] = startTime

                    return True
                    # else:
                    # raise Exception("Error grabbing job: %s" % jresult['error'])
                    # else:
                    #   self.getOurInfo() # see if our status has changed.
        else:
            raise Exception("Error finding new job: %s" % result['error'])
        return False

def main():
    bee = BumbleBee()
    bee.main()


if __name__ == "__main__":
    sys.exit(main())