from bumblebee.host.configurations import HostConfiguration


class TestHostConfiguration(object):
    def test_default_parameters_exist(self, resolver):
        config = resolver(HostConfiguration)

        assert "servers" in config
