from urllib.parse import urljoin

import requests

from bumblebee.host.configurations import HostConfiguration


class AccessTokenNotFound(Exception):
    pass


class RestApi(object):
    def __init__(self,
                 config: HostConfiguration):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def post(self, url, data=None):
        json = data if data is not None else {}

        if "access_token" in self.config:
            access_token = self.config["access_token"]

            self.session.headers.update({"Authorization": f"Bearer {access_token}"})

        full_url = urljoin(self.config["server"], url)
        return self.session.post(full_url, json=json)
