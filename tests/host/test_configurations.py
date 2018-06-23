import tempfile
from unittest.mock import Mock

from appdirs import AppDirs

from bumblebee.host.configurations import HostConfiguration


class TestHostConfiguration(object):
    def test_default_parameters_exist(self, resolver):
        app_mock = Mock(AppDirs)

        resolver.instance(AppDirs, app_mock)
        app_mock.user_config_dir = tempfile.mkdtemp()

        config = resolver(HostConfiguration)

        assert "server" in config
