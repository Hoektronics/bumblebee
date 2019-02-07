from urllib.parse import urljoin

import requests

from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.framework.ioc import Resolver


class AccessTokenNotFound(Exception):
    pass


class RestApi(object):
    def __init__(self,
                 config: HostConfiguration):
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.config = config

    def with_token(self):
        resolver = Resolver.get()

        if "access_token" not in self.config:
            raise AccessTokenNotFound("Access token not found in host configuration")

        access_token = self.config["access_token"]

        rest_api = RestApi(self.config)
        rest_api._headers = self._headers.copy()

        rest_api._headers["Authorization"] = f"Bearer {access_token}"

        return rest_api

    def get(self, url):
        full_url = urljoin(self.config["server"], url)
        return requests.get(full_url, headers=self._headers)

    def post(self, url, data=None):
        json = data if data is not None else {}

        full_url = urljoin(self.config["server"], url)
        return requests.post(full_url, json=json, headers=self._headers)

    def put(self, url, data=None):
        json = data if data is not None else {}

        full_url = urljoin(self.config["server"], url)
        return requests.put(full_url, json=json, headers=self._headers)
