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

    @property
    def access_token(self):
        if "access_token" not in self._server_config:
            return None
        return self._server_config["access_token"]

    @access_token.setter
    def access_token(self, value):
        self._server_config["access_token"] = value
