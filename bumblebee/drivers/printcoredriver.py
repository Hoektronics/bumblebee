import time
import logging
import os
import sys
from threading import Thread
import re

from bumblebee.drivers import bumbledriver

# Disabling this because of a bug in printrun
lib_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'Printrun')
sys.path.append(lib_path)

from printrun import printcore
from printrun import gcoder

def scanPorts():
    try:
        import serial.tools.list_ports

        return list(serial.tools.list_ports.comports())
    except ImportError:
        return None
    except Exception as ex:
        log = logging.getLogger('botqueue')
        log.error("Printcore cannot scan serial ports.")
        log.exception(ex)
        return None


# todo: this whole thing sucks.  we need a much better way to interface with this.
class printcoredriver(bumbledriver.bumbledriver):
    def __init__(self, config):
        super(printcoredriver, self).__init__(config)
        self.log = logging.getLogger('botqueue')
        self.printThread = None
        self.temperatures = {}

    def startPrint(self, jobfile):
        self.p = printcore.printcore()
        self.p.tempcb = self._tempCallback
        self.p.errorcb = self._errorCallback
        self.p.loud = False
        try:
            self.printing = True
            self.connect()
            while not self.isConnected():
                time.sleep(1)
                self.log.debug("Waiting for driver to connect.")
            self.gcoder = gcoder.GCode(jobfile.localFile)
            self.p.startprint(self.gcoder)
            self.printThread = Thread(target=self.printThreadEntry).start()
        except Exception as ex:
            self.log.error("Error starting print: %s" % ex)
            self.disconnect()
            raise ex

    # this doesn't do much, just a thread to watch our thread indirectly.
    def executeFile(self):
        while (self.p.printing):
            self.printing = self.p.printing

            time.sleep(0.1)
        time.sleep(1)
        self.disconnect()

    def _errorCallback(self,error):
        self.errorMessage = error
        self.disconnect()
        raise Exception(self.errorMessage)

    def getPercentage(self):
        if self.p.mainqueue is not None:
            return float(self.p.queueindex) / float(len(self.p.mainqueue)) * 100
        else:
            return 0

    def pause(self):
        self.p.pause()
        super(printcoredriver, self).pause()

    def resume(self):
        self.p.resume()
        super(printcoredriver, self).resume()

    def reset(self):
        self.p.reset()
        super(printcoredriver, self).reset()

    def isConnected(self):
        return self.p.online and self.p.printer

    def stop(self):
        try:
            self.p.cancelprint()
            self.disconnect()
        except AttributeError as ex:
            self.log.error(ex)

    def getTemperature(self):
        return self.temperatures

    def _tempCallback(self, line):
        #look for our extruder temp strings
        matches = re.findall('T:([0-9]*\.?[0-9]+)', line)
        if matches:
            self.temperatures['extruder'] = matches[0]

        matches = re.findall('T:([0-9]*\.?[0-9]+) /([0-9]*\.?[0-9]+)', line)
        if matches:
            self.temperatures['extruder'] = matches[0][0]
            self.temperatures['extruder_target'] = matches[0][1]

        # look for our bed temp strings
        matches = re.findall('B:([0-9]*\.?[0-9]+)', line)
        if matches:
            self.temperatures['bed'] = matches[0]

        matches = re.findall('B:([0-9]*\.?[0-9]+) /([0-9]*\.?[0-9]+)', line)
        if matches:
            self.temperatures['bed'] = matches[0][0]
            self.temperatures['bed_target'] = matches[0][1]

    def connect(self):
        if not self.isConnected():
            self.p.connect(self.config['port'], self.config['baud'])
            super(printcoredriver, self).connect()

    def disconnect(self):
        if self.isConnected():
            if self.printThread is not None:
                self.printThread.join(10)
            self.p.disconnect()
            super(printcoredriver, self).disconnect()
