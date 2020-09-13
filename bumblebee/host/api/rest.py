from urllib.parse import urljoin

import requests

from bumblebee.host.api.server import Server


class AccessTokenNotFound(Exception):
    pass


class RestApi(object):
    def __init__(self,
                 server: Server):
        self._server = server
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def post(self, url, data=None):
        json = data if data is not None else {}

        if self._server.access_token is not None:
            access_token = self._server.access_token

            self.session.headers.update({"Authorization": f"Bearer {access_token}"})

        full_url = urljoin(self._server.url, url)
        return self.session.post(full_url, json=json)
