import json
import logging
import shutil
import time
import threading

import os
from bumblebee import camera_control
from bumblebee import drivers
from bumblebee import ginsu
from bumblebee import hive


class WorkerBee:
    sleepTime = 0.5

    def __init__(self, api, data):
        self.config = data['driver_config']
        self.bot_name = self.bot_name

        # we need logging!
        self.log = logging.getLogger('botqueue')

        self.api = api
        self.data = data
        self.data_lock = threading.RLock()

        self.driver = None
        self.cacheHit = False
        self.running = False
        self.job_file = None

        self.info("Bot startup")

        # load up our driver
        self.initialize_driver()

        # look at our current state to check for problems.
        self.startup_check_state()


        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def startup_check_state(self):
        # we shouldn't startup in a working state... that implies some sort of error.
        if self.data['status'] == 'working':
            self.error_mode("Startup in %s mode, dropping job # %s" % (self.data['status'], self.data['job']['id']))

    def error_mode(self, error):
        self.error("Error mode: %s" % error)

        # drop 'em if you got em.
        try:
            self.drop_job(error)
        except Exception as ex:
            self.exception(ex)

        # take the bot offline.
        self.info("Setting bot status as error.")
        result = self.api.updateBotInfo({'bot_id': self.data['id'], 'status': 'error', 'error_text': error})
        if result['status'] == 'success':
            self.update(result['data'])
        else:
            self.error("Error talking to mothership: %s" % result['error'])

    def initialize_driver(self):
        try:
            self.driver = self.driver_factory()
        except Exception as ex:
            self.exception(ex)  # dump a stacktrace for debugging.
            self.error_mode(ex)

    def driver_factory(self):

        module_name = 'bumblebee.drivers.' + self.config['driver'] + 'driver'
        __import__(module_name)

        if self.config['driver'] == 's3g':
            return drivers.s3gdriver.s3gdriver(self.config)
        elif self.config['driver'] == 'printcore':
            return drivers.printcoredriver.printcoredriver(self.config)
        elif self.config['driver'] == 'dummy':
            return drivers.dummydriver.dummydriver(self.config)
        else:
            raise Exception("Unknown driver specified.")

    # this is our entry point for the worker subprocess
    def run(self):
        last_webcam_update_time = time.time()
        try:
            # okay, we're off!
            self.running = True
            while self.running:
                # slicing means we need to slice our job.
                if self.data['status'] == 'slicing':
                    if self.data['job']['slicejob']['status'] == 'slicing' and self.config['can_slice']:
                        self.slice_job()
                # working means we need to process a job.
                elif self.data['status'] == 'working':
                    self.process_job()
                    # self.getOurInfo() # if there was a problem with the job,
                    # we'll find it by pulling in a new bot state and looping again.
                    self.debug("Bot finished @ state %s" % self.data['status'])

                # upload a webcam pic every so often.
                if time.time() - lastWebcamUpdate > 60:
                    outputName = "bot-%s.jpg" % self.data['id']
                    if self.takePicture(outputName):
                        fullImgPath = hive.getImageDirectory(outputName)
                        self.api.webcamUpdate(fullImgPath, bot_id=self.data['id'])
                    lastWebcamUpdate = time.time()

                time.sleep(self.sleepTime)  # sleep for a bit to not hog resources
        except Exception as ex:
            self.exception(ex)
            self.driver.stop()
            raise ex

        self.debug("Exiting.")

    def is_alive(self):
        return self.thread.is_alive()

    def update(self, new_data):
        with self.data_lock:
            if new_data['status'] != self.data['status']:
                self.info("Changing status from %s to %s" % (self.data['status'], new_data['status']))

                # okay, are we transitioning from paused to unpaused?
                if new_data['status'] == 'paused':
                    self.pause_job()
                if self.data['status'] == 'paused' and new_data['status'] == 'working':
                    self.resume_job()

            status = new_data['status']

            # did our status change?  if so, make sure to stop our currently running job.
            if self.data['status'] == 'working' or self.data['status'] == 'paused':
                if status in ('idle', 'offline', 'error', 'maintenance'):
                    self.info("Stopping job.")
                    self.stop_job()

            # did we get a new config?
            if json.dumps(new_data['driver_config']) != json.dumps(self.config):
                self.log.info("Driver config has changed, updating.")
                self.config = new_data['driver_config']
                self.initialize_driver()

            self.data = new_data

    # get bot info from the mothership
    def get_our_info(self):
        self.debug("Looking up bot # %s." % self.data['id'])

        result = self.api.getBotInfo(self.data['id'])
        if result['status'] == 'success':
            self.update(result['data'])
        else:
            self.error("Error looking up bot info: %s" % result['error'])
            raise Exception("Error looking up bot info: %s" % result['error'])

    def get_new_job(self):
        find_job_result = self.api.findNewJob(self.data['id'], self.config['can_slice'])
        if find_job_result['status'] == 'success':
            if len(find_job_result['data']):
                job = find_job_result['data']
                grab_job_result = self.api.grabJob(self.data['id'], job['id'], self.config['can_slice'])

                if grab_job_result['status'] == 'success':
                    self.data['job'] = job

                    return True
        else:
            raise Exception("Error finding new job: %s" % find_job_result['error'])
        return False

    def slice_job(self):
        # download our slice file
        slice_file = self.download_file(self.data['job']['slicejob']['input_file'])

        # create and run our slicer
        g = ginsu.Ginsu(slice_file, self.data['job']['slicejob'])
        g.slice()

        # watch the slicing progress
        local_update = 0
        last_update = 0
        while g.isRunning():
            if not self.running or self.data['status'] != 'slicing':
                self.debug("Stopping slice job")
                g.stop()
                return

            # notify the local mothership of our status.
            if time.time() - local_update > 0.5:
                self.data['job']['progress'] = g.getProgress()
                local_update = time.time()

            # occasionally update home base.
            if time.time() - last_update > 15:
                last_update = time.time()
                self.api.updateJobProgress(self.data['job']['id'], "%0.5f" % g.getProgress())

            time.sleep(self.sleepTime)

        # how did it go?
        sushi = g.sliceResult

        # move the file to the cache directory
        cache_dir = hive.getCacheDirectory()
        base_file_name = os.path.splitext(os.path.basename(self.data['job']['slicejob']['input_file']['name']))[0]
        md5sum = hive.md5sumfile(sushi.output_file)
        upload_file = "%s%s-%s.gcode" % (cache_dir, md5sum, base_file_name)
        self.debug("Moved slice output to %s" % upload_file)
        shutil.copy(sushi.output_file, upload_file)

        # update our slice job progress and pull in our update info.
        self.info("Finished slicing, uploading results to main site.")
        result = self.api.updateSliceJob(job_id=self.data['job']['slicejob']['id'], status=sushi.status,
                                         output=sushi.output_log, errors=sushi.error_log, filename=upload_file)

        # now pull in our new data.
        self.update(result['data'])

    def download_file(self, file_info):
        my_file = hive.URLFile(file_info)

        local_update = 0
        try:
            my_file.load()

            while my_file.getProgress() < 100:
                # notify the local mothership of our status.
                if time.time() - local_update > 0.5:
                    self.data['job']['progress'] = my_file.getProgress()
                    local_update = time.time()
                time.sleep(self.sleepTime)
            # okay, we're done... send it back.
            return my_file
        except Exception as ex:
            self.exception(ex)

    def process_job(self):
        # go get 'em, tiger!
        self.job_file = self.download_file(self.data['job']['file'])

        # notify the mothership of download completion
        self.api.downloadedJob(self.data['job']['id'])

        local_update = 0
        last_update = 0
        last_temp = 0
        latest = 0
        try:
            self.driver.startPrint(self.job_file)
            while self.driver.isRunning():
                latest = self.driver.getPercentage()

                # look up our temps?
                if time.time() - last_temp > 1:
                    last_temp = time.time()
                    temps = self.driver.getTemperature()

                # notify the mothership of our status.
                if time.time() - local_update > 0.5:
                    local_update = time.time()
                    self.data['job']['progress'] = latest
                    self.data['job']['temperature'] = temps

                # did we get paused?
                while self.data['status'] == 'paused':
                    time.sleep(self.sleepTime)

                # should we bail out of here?
                if not self.running or self.data['status'] != 'working':
                    self.stop_job()
                    return

                # occasionally update home base.
                if time.time() - last_update > 15:
                    last_update = time.time()
                    self.update_home_base(latest, temps)

                if self.driver.hasError():
                    raise Exception(self.driver.getErrorMessage())

                time.sleep(self.sleepTime)

            # did our print finish while running?
            if self.running and self.data['status'] == 'working':
                self.info("Print finished.")

                # send up a final 100% info.
                self.data['job']['progress'] = 100.0
                self.update_home_base(latest, temps)

                # finish the job online, and mark as completed.
                result = self.api.completeJob(self.data['job']['id'])
                if result['status'] == 'success':
                    self.update(result['data']['bot'])
                else:
                    self.error("Error notifying mothership: %s" % result['error'])
        except Exception as ex:
            self.exception(ex)
            self.error_mode(ex)

    def pause_job(self):
        self.info("Pausing job.")
        self.driver.pause()

    def resume_job(self):
        self.info("Resuming job.")
        self.driver.resume()

    def stop_job(self):
        if self.driver is not None and not self.driver.hasError():
            if self.driver.isRunning() or self.driver.isPaused():
                self.info("stopping driver.")
                self.driver.stop()

    def drop_job(self, error=None):
        self.stop_job()

        if len(self.data['job']) and self.data['job']['id']:
            result = self.api.drop_job(self.data['job']['id'], error)
            self.info("Dropping existing job.")
            if result['status'] == 'success':
                self.get_our_info()
            else:
                raise Exception("Unable to drop job: %s" % result['error'])

    def shutdown(self):
        self.info("Shutting down.")
        if self.data['status'] == 'working' and self.data['job']['id']:
            self.drop_job(error="Shutting down.")
        self.running = False

    def debug(self, msg):
        self.log.debug("%s: %s" % (self.bot_name, msg))

    def info(self, msg):
        self.log.info("%s: %s" % (self.bot_name, msg))

    def warning(self, msg):
        self.log.warning("%s: %s" % (self.bot_name, msg))

    def error(self, msg):
        self.log.error("%s: %s" % (self.bot_name, msg))

    def exception(self, msg):
        self.log.exception("%s: %s" % (self.bot_name, msg))

    def update_home_base(self, latest, temps):
        self.info("print: %0.2f%%" % float(latest))
        outputName = "bot-%s.jpg" % self.data['id']

        if self.takePicture(outputName):
            fullImgPath = hive.getImageDirectory(outputName)
            self.api.webcamUpdate(fullImgPath,
                                  job_id=self.data['job']['id'],
                                  progress="%0.5f" % float(latest),
                                  temps=temps)
        else:
            self.api.updateJobProgress(self.data['job']['id'], "%0.5f" % float(latest), temps)

    def takePicture(self, filename):
        # create our command to do the webcam image grabbing
        try:

            # do we even have a webcam config setup?
            if 'webcam' in self.config:
                if self.data['status'] == 'working':
                    watermark = "%s :: %0.2f%% :: BotQueue.com" % (
                        self.config['name'],
                        float(self.data['job']['progress'])
                    )
                else:
                    watermark = "%s :: BotQueue.com" % self.config['name']

                device = self.config['webcam']['device']

                brightness = 50
                if 'brightness' in self.config['webcam']:
                    brightness = self.config['webcam']['brightness']

                contrast = 50
                if 'contrast' in self.config['webcam']:
                    contrast = self.config['webcam']['contrast']
                return camera_control.takePicture(device=device,
                                                  watermark=watermark,
                                                  output=filename,
                                                  brightness=brightness,
                                                  contrast=contrast)

            else:
                return False

        # main try/catch block
        except Exception as ex:
            self.exception(ex)
            return False
