import time


class DummyDriver(object):
    def __init__(self, config):
        self.command_delay = 100

        if config is not None and "command_delay" in config:
            self.command_delay = config["command_delay"]

    def connect(self):
        pass

    def disconnect(self):
        pass

    def run(self, filename):
        print(f"Executing {filename}")
        with open(filename, 'rb') as fh:
            lines = fh.readlines()
            for line in lines:
                print(f"Gcode: {line.strip()}")
                time.sleep(self.command_delay / 1000.0)
