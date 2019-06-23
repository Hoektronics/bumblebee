import os
from logging import FileHandler

from bumblebee.host.framework.logging import HostLogging


class TestHostLogging(object):
    def test_logging_adds_file_handler_once_per_name(self, resolver, user_log_dir):
        host_log_path = os.path.join(user_log_dir, 'host.log')

        host_logging: HostLogging = resolver(HostLogging)

        log_foo_1 = host_logging.get_logger("foo")

        assert len(log_foo_1.handlers) == 1
        assert isinstance(log_foo_1.handlers[0], FileHandler)
        assert log_foo_1.handlers[0].stream.name == host_log_path

        log_foo_2 = host_logging.get_logger("foo")

        assert len(log_foo_2.handlers) == 1
        assert log_foo_2.handlers[0] is log_foo_1.handlers[0]

    def test_logging_adds_different_file_handler_for_different_name(self, resolver):
        host_logging: HostLogging = resolver(HostLogging)

        log_foo = host_logging.get_logger("foo")

        log_bar = host_logging.get_logger("bar")

        assert log_foo.handlers[0] is not log_bar.handlers[0]
