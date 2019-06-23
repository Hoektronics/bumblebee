from bumblebee.host.framework.configuration import Configuration


class TestConfiguration(object):
    def test_can_work_with_keys(self, resolver):
        config = Configuration("test")

        assert "key" not in config

        config["key"] = "testing"

        assert "key" in config
        assert config["key"] == "testing"

        del config["key"]

        assert "key" not in config

    def test_configuration_auto_saves_on_set(self, resolver):
        config_first = Configuration("test")

        assert "key" not in config_first
        config_first["key"] = "value"

        config_second = Configuration("test")
        assert "key" in config_second
        assert config_second["key"] == "value"

    def test_configuration_auto_saves_on_delete(self, resolver):
        config_first = Configuration("test")

        assert "key" not in config_first
        config_first["key"] = "value"

        del config_first["key"]

        config_second = Configuration("test")
        assert "key" not in config_second

    def test_will_make_directory_if_non_existent(self, resolver):
        config_first = Configuration("test")

        assert "key" not in config_first
        config_first["key"] = "value"

        config_second = Configuration("test")
        assert "key" in config_second
        assert config_second["key"] == "value"
