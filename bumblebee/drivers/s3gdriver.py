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
        temperature_count = 0

        while self.currentProgress < self.totalPayloads and self.printing:
            payload = self.convert_payload(payloads[self.currentProgress])
            temperature_count += 1
            try:
                if temperature_count == 10:
                    self.temperature = self.s3g.get_toolhead_temperature(0)
                    temperature_count = 0
                self.s3g.writer.send_command(payload)
                self.currentProgress += 1
            except makerbot_driver.BufferOverflowError as ex:
                time.sleep(.5)

        # Wait for the print to finish
        while not self.s3g.is_finished():
            time.sleep(1)

        self.s3g.build_end_notification()

    def convert_payload(self, payload):
        host_command = payload[0]
        host_payload = payload[1:]
        host_command_format = makerbot_driver.FileReader.hostFormats[host_command]
        result = self.convert(host_command, host_command_format, host_payload);

        if host_command == 136:
            slave_command = host_payload[1]
            slave_payload = host_payload[len(host_command_format):]
            slave_command_format = makerbot_driver.FileReader.slaveFormats[slave_command]
            result.extend(self.convert(slave_command, slave_command_format, slave_payload))

        return result

    def convert(self, command, command_format, payload):
        struct_formats = makerbot_driver.FileReader.structFormats
        result = [command]
        for data_format, data in zip(command_format, payload):
            if data_format == 'B':
                result.extend([data])
                continue

            old_format = data_format
            new_format = '<' + str(struct_formats[data_format]) + 'B'

            if data_format == 's':
                old_format = str(len(data)) + 's'
                new_format = "<" + str(len(data)) + 'B'

            new_structure = struct.unpack(new_format, struct.pack(old_format, data))
            result.extend(new_structure)

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
