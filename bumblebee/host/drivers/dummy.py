import time


class DummyDriver(object):
    def __init__(self, config):
        self.command_delay = 100

        if config is not None and "command_delay" in config:
            self.command_delay = config["command_delay"]

        self._time_since_last_update = 0

    def connect(self):
        pass

    def disconnect(self):
        pass

    def run(self, filename, **kwargs):
        if "update_job_progress" in kwargs:
            update_job_progress = kwargs["update_job_progress"]
        else:
            update_job_progress = None

        print(f"Executing {filename}")
        with open(filename, 'rb') as fh:
            lines = fh.readlines()
            for index in range(len(lines)):
                line = lines[index]
                print(f"Gcode: {line.strip()}")
                time.sleep(self.command_delay / 1000.0)

                if time.time() > self._time_since_last_update + 5:
                    progress = 100.0 * (float(index) / float(len(lines)))
                    if update_job_progress is not None:
                        update_job_progress(progress)

                    self._time_since_last_update = time.time()
