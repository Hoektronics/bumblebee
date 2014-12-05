import logging
import os
import shutil
import struct
import sys
import time

from bumblebee import hive
from bumblebee.drivers import bumbledriver
from threading import Thread, Condition

old_lib_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + os.sep + 's3g')
if os.path.exists(old_lib_path):
    shutil.rmtree(old_lib_path)

lib_path = hive.getEngine('s3g', type="driver", repo="https://github.com/makerbot/s3g")
sys.path.append(lib_path)

# this has to come after the above code
try:
    import makerbot_driver
    import serial
except Exception as ex:
    raise Exception("Please use Makerbot's version of pyserial")


class s3gdriver(bumbledriver.bumbledriver):
    def __init__(self, config):
        super(s3gdriver, self).__init__(config)

        self.currentProgress = 0
        self.totalPayloads = 1
        self.log = logging.getLogger('botqueue')
        self.s3g = None
        self.printThread = None
        self.temperature = None

    def startPrint(self, jobfile):
        try:
            self.jobfile = jobfile
            self.printing = True
            self.connect()
            while not self.isConnected():
                time.sleep(1)
                self.log.debug("Waiting for driver to connect.")
            self.printThread = Thread(target=self.printThreadEntry).start()
        except Exception as ex:
            self.log.error("Error starting print: %s" % ex)
            self.disconnect()
            raise ex

    def executeFile(self):
        self.s3g.init()

        self.s3g.build_start_notification("BotQueue!")

        reader = makerbot_driver.FileReader.FileReader()
        reader.file = self.jobfile.localFile
        payloads = reader.ReadFile()

        self.currentProgress = 0
        self.totalPayloads = len(payloads)
        temperatureCount = 0

        while self.currentProgress < self.totalPayloads and self.printing:
            payload = self.convertPayload(payloads[self.currentProgress])
            temperatureCount += 1
            try:
                if temperatureCount == 10:
                    self.temperature = self.s3g.get_toolhead_temperature(0)
                    temperatureCount = 0
                self.s3g.writer.send_command(payload)
                self.currentProgress += 1
            except makerbot_driver.BufferOverflowError as ex:
                time.sleep(.5)

        # Wait for the print to finish
        while not self.s3g.is_finished():
            time.sleep(1)

        self.s3g.build_end_notification()

    def convertPayload(self, payload):
        cmd, payload = payload[0], payload[1:]
        cmdFormat = makerbot_driver.FileReader.hostFormats[cmd]
        structFormats = makerbot_driver.FileReader.structFormats
        result = []
        for fmt, data in zip(cmdFormat, payload):
            if(fmt == 'B'):
                result.append(data)
                continue
            if fmt == 's':
                fmt = str(len(data)) + "s"
                newFormat = "<" + str(len(data)) + "B"
            else:
                newFormat = "<" + str(structFormats[fmt]) + "B"
            result.extend(struct.unpack(newFormat, struct.pack(fmt, data)))
        return result

    def getPercentage(self):
        return float(self.currentProgress) / float(self.totalPayloads) * 100

    def connect(self):
        if not self.isConnected():
            try:
                self.s3g = makerbot_driver.s3g.from_filename(
                    port=self.config['port'],
                    baudrate=self.config['baud'],
                    condition=Condition()
                )

                super(s3gdriver, self).connect()

            except serial.SerialException as ex:
                self.s3g = None
                raise Exception(ex.message)

    def getTemperature(self):
        if self.temperature is not None:
            return {'extruder': self.temperature}
        return None

    def isConnected(self):
        if self.s3g is not None:
            return self.s3g.is_open()
        else:
            return False

    def disconnect(self):
        if self.isConnected():
            self.s3g.close()
            self.s3g = None
            super(s3gdriver, self).disconnect()

    def pause(self):
        if self.isConnected():
            self.s3g.pause()
            super(s3gdriver, self).pause()

    def resume(self):
        if self.isConnected():
            # Pause resumes if it's already paused
            self.s3g.pause()
            super(s3gdriver, self).resume()

    def stop(self):
        self.printing = False
        if self.isConnected():
            # Sleep so no knew commands are sent
            time.sleep(1)
            self.s3g.abort_immediately()
            super(s3gdriver, self).stop()

    def reset(self):
        if self.isConnected():
            self.s3g.reset()
            super(s3gdriver, self).reset()
