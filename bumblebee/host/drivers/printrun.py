import time

from printrun.printcore import printcore
from printrun import gcoder


class PrintrunDriver(object):
    def __init__(self, config):
        self.serial_port = config["connection"]["port"]
        self.baud_rate = None

        if "baud" in config["connection"]:
            self.baud_rate = config["connection"]["baud"]

        self.printcore = printcore()

    def connect(self):
        self.printcore.connect(self.serial_port, self.baud_rate)

        while not self.printcore.online:
            print("Printer is not online yet")
            time.sleep(2)

    def disconnect(self):
        self.printcore.disconnect()

    def run(self, filename):
        with open(filename, 'rb') as fh:
            gcode = [i.strip().decode("utf-8") for i in fh.readlines()]

        gcode = gcoder.LightGCode(gcode)

        self.printcore.startprint(gcode)

        while self.printcore.printing:
            time.sleep(5)
