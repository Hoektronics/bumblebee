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

    def test_sub_dictionary_auto_saves_on_set(self, resolver):
        config_first = Configuration("test")

        config_first["sub"] = {}
        config_first["sub"]["key"] = "value"

        config_second = Configuration("test")
        assert "sub" in config_second
        assert "key" in config_second["sub"]
        assert config_second["sub"]["key"] == "value"

    def test_sub_dictionary_can_be_set_back_to_different_parent_key(self, resolver):
        config = Configuration("test")

        config["sub"] = {}
        sub = config["sub"]

        sub["key"] = "value"

        config["sub2"] = sub

        assert "sub" in config
        assert "key" in config["sub"]
        assert config["sub"]["key"] == "value"
        assert "sub2" in config
        assert "key" in config["sub2"]
        assert config["sub2"]["key"] == "value"
