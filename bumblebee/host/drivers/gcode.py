class GcodeDriver(object):
    def __init__(self, config):
        self.serial_port = config["connection"]["port"]
        self.baud_rate = None

        if "baud" in config["connection"]:
            self.baud_rate = config["connection"]["baud"]