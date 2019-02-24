import time

from printrun.printcore import printcore
from printrun import gcoder


class PrintrunDriver(object):
    def __init__(self, config):
        self.serial_port = config["connection"]["port"]
        self.baud_rate = None

        if "baud" in config["connection"]:
            self.baud_rate = config["connection"]["baud"]

    def run(self, filename):
        with open(filename, 'rb') as fh:
            gcode = [i.strip().decode("utf-8") for i in fh.readlines()]

        gcode = gcoder.LightGCode(gcode)

        p = printcore(self.serial_port, self.baud_rate)

        while not p.online:
            print("Printer is not online yet")
            time.sleep(2)

        p.startprint(gcode)

        while p.printing:
            time.sleep(5)
