from bumblebee.host.configurations import HostConfiguration


class Server(object):
    def __init__(self,
                 url,
                 config: HostConfiguration):
        self._url = url

        if self._url not in config["servers"]:
            config["servers"][self._url] = {}

        self._server_config = config["servers"][self._url]

    @property
    def url(self):
        return self._url

    def _fetch_from_config(self, key):
        if key not in self._server_config:
            return None
        return self._server_config[key]

    @property
    def access_token(self):
        return self._fetch_from_config("access_token")

    @access_token.setter
    def access_token(self, value):
        self._server_config["access_token"] = value

    @property
    def request_id(self):
        return self._fetch_from_config("request_id")

    @request_id.setter
    def request_id(self, value):
        self._server_config["request_id"] = value

    @request_id.deleter
    def request_id(self):
        del self._server_config["request_id"]

    @property
    def host_id(self):
        return self._fetch_from_config("host_id")

    @host_id.setter
    def host_id(self, value):
        self._server_config["host_id"] = value

    @property
    def host_name(self):
        return self._fetch_from_config("host_name")

    @host_name.setter
    def host_name(self, value):
        self._server_config["host_name"] = value
