from bumblebee.host.drivers.dummy import DummyDriver
from bumblebee.host.drivers.printrun import PrintrunDriver
from bumblebee.host.framework.ioc import Resolver


class InvalidDriver(Exception):
    pass


class DriverFactory(object):
    def __init__(self,
                 resolver: Resolver):
        self.resolver = resolver

    def get(self, driver_setup):
        if driver_setup is None:
            raise InvalidDriver("Driver configuration was None")

        if "type" not in driver_setup:
            raise InvalidDriver("No type listed in driver configuration")

        driver_type = driver_setup["type"]
        driver_config = driver_setup["config"] if "config" in driver_setup else None

        if driver_type == "dummy":
            return self.resolver(DummyDriver, config=driver_config)

        if driver_type == "gcode":
            return self.resolver(PrintrunDriver, config=driver_config)