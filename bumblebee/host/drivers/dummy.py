class DummyDriver(object):
    def __init__(self):
        pass

    def run(self, filename):
        print(f"Executing {filename}")
        with open(filename, 'rb') as fh:
            lines = fh.readlines()
            for line in lines:
                print(f"Gcode: {line.strip()}")