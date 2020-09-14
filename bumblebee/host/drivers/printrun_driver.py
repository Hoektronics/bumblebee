import time

from bumblebee.host.drivers.printrun.printcore import printcore
from bumblebee.host.drivers.printrun.gcoder import LightGCode


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

    def run(self, filename, **kwargs):
        if "update_job_progress" in kwargs:
            update_job_progress = kwargs["update_job_progress"]
        else:
            update_job_progress = None

        with open(filename, 'rb') as fh:
            gcode = [i.strip().decode("utf-8") for i in fh.readlines()]

        gcode = LightGCode(gcode)

        self.printcore.startprint(gcode)

        while self.printcore.printing:
            time.sleep(5)

            progress = 100.0 * (float(self.printcore.queueindex) / float(len(self.printcore.mainqueue)))
            if update_job_progress is not None:
                update_job_progress(progress)
