import os
import tempfile
from unittest.mock import Mock

from appdirs import AppDirs

from bumblebee.host.framework import resolver
from bumblebee.host.framework.configuration import Configuration


class TestConfiguration(object):
    def test_can_work_with_keys(self):
        app_mock = Mock(AppDirs)

        resolver.instance(AppDirs, app_mock)
        app_mock.user_config_dir = tempfile.mkdtemp()

        config = Configuration("test")

        assert "key" not in config

        config["key"] = "testing"

        assert "key" in config
        assert config["key"] == "testing"

        del config["key"]

        assert "key" not in config

    def test_can_save_configuration(self):
        app_mock = Mock(AppDirs)

        resolver.instance(AppDirs, app_mock)
        app_mock.user_config_dir = tempfile.mkdtemp()

        config_first = Configuration("test")

        assert "key" not in config_first
        config_first["key"] = "value"
        config_first.save()

        config_second = Configuration("test")
        assert "key" in config_second
        assert config_second["key"] == "value"

    def test_will_make_diretory_if_non_existent(self):
        app_mock = Mock(AppDirs)

        resolver.instance(AppDirs, app_mock)
        app_mock.user_config_dir = os.path.join(tempfile.mkdtemp(), 'some_sub_dir')

        config_first = Configuration("test")

        assert "key" not in config_first
        config_first["key"] = "value"
        config_first.save()

        config_second = Configuration("test")
        assert "key" in config_second
        assert config_second["key"] == "value"
