from bumblebee.host.api.server import Server
from bumblebee.host.configurations import HostConfiguration


class TestServer(object):
    url = "http://example.test"

    def test_server_config_is_created(self, resolver):
        config = resolver(HostConfiguration)

        assert self.url not in config["servers"]

        resolver(Server, url=self.url)

        assert self.url in config["servers"]

    def test_url(self, resolver):
        server = resolver(Server, url=self.url)

        assert server.url == self.url

    def test_access_token(self, resolver):
        config = resolver(HostConfiguration)
        server = resolver(Server, url=self.url)

        access_token = "my_access_token"
        server.access_token = access_token

        assert server.access_token == access_token
        assert config["servers"][self.url]["access_token"] == access_token

    def test_request_id(self, resolver):
        config = resolver(HostConfiguration)
        server = resolver(Server, url=self.url)

        request_id = "my_request_id"
        server.request_id = request_id

        assert server.request_id == request_id
        assert config["servers"][self.url]["request_id"] == request_id

        del server.request_id

        assert server.request_id is None
        assert "request_id" not in config["servers"][self.url]

    def test_host_id(self, resolver):
        config = resolver(HostConfiguration)
        server = resolver(Server, url=self.url)

        host_id = 5
        server.host_id = host_id

        assert server.host_id == host_id
        assert config["servers"][self.url]["host_id"] == host_id

    def test_host_name(self, resolver):
        config = resolver(HostConfiguration)
        server = resolver(Server, url=self.url)

        host_name = "my_host_name"
        server.host_name = host_name

        assert server.host_name == host_name
        assert config["servers"][self.url]["host_name"] == host_name
