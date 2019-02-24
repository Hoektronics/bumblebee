import pytest

from bumblebee.host.drivers.driver_factory import DriverFactory, InvalidDriver
from bumblebee.host.drivers.dummy import DummyDriver
from bumblebee.host.drivers.printrun import PrintrunDriver


class TestDriverFactory(object):
    def test_a_none_configuration_fails(self, resolver):
        factory = resolver(DriverFactory)

        with pytest.raises(InvalidDriver):
            factory.get(None)

    def test_a_configuration_without_a_type_fails(self, resolver):
        factory = resolver(DriverFactory)

        with pytest.raises(InvalidDriver):
            factory.get({})

    def test_driver_string_dummy_gives_dummy_driver(self, resolver):
        factory = resolver(DriverFactory)

        driver = factory.get({
            "type": "dummy"
        })

        assert isinstance(driver, DummyDriver)

    def test_dummy_driver_gets_configuration(self, resolver):
        factory = resolver(DriverFactory)

        driver: DummyDriver = factory.get({
            "type": "dummy",
            "config": {
                "command_delay": 200
            }
        })

        assert isinstance(driver, DummyDriver)
        assert driver.command_delay == 200

    def test_driver_string_gcode_gives_printrun_driver(self, resolver):
        factory = resolver(DriverFactory)

        driver: PrintrunDriver = factory.get({
            "type": "gcode",
            "config": {
                "connection": {
                    "type": "serial",
                    "port": "/dev/testSerial"
                }
            }
        })

        assert isinstance(driver, PrintrunDriver)
        assert driver.serial_port == "/dev/testSerial"
        assert driver.baud_rate is None

    def test_printrun_driver_will_populate_baud_rate(self, resolver):
        factory = resolver(DriverFactory)

        driver: PrintrunDriver = factory.get({
            "type": "gcode",
            "config": {
                "connection": {
                    "type": "serial",
                    "port": "/dev/testSerial",
                    "baud": 250000
                }
            }
        })

        assert isinstance(driver, PrintrunDriver)
        assert driver.serial_port == "/dev/testSerial"
        assert driver.baud_rate == 250000
