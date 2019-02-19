import time

from printrun.printcore import printcore
from printrun import gcoder

class PrintrunDriver(object):
    def __init__(self):
        pass

    def run(self, filename):
        with open(filename, 'rb') as fh:
            gcode = [i.strip().decode("utf-8") for i in fh.readlines()]

        gcode = gcoder.LightGCode(gcode)

        p = printcore('/dev/cu.usbmodem141301', 250000)

        while not p.online:
            print("Printer is not online yet")
            time.sleep(2)

        p.startprint(gcode)

        while p.printing:
            time.sleep(5)