import requests

from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.framework.ioc import Resolver


class AccessTokenNotFound(Exception):
    pass


class BotQueueApi(object):
    def __init__(self):
        self._headers = {}

    def with_token(self):
        resolver = Resolver.get()
        config = resolver(HostConfiguration)

        if "access_token" not in config:
            raise AccessTokenNotFound("Access token not found in host configuration")

        access_token = config["access_token"]

        botqueue_api = BotQueueApi()
        botqueue_api._headers = self._headers.copy()

        botqueue_api._headers["Authorization"] = f"Bearer {access_token}"

        return botqueue_api

    def get(self, url):
        return requests.get(url, headers=self._headers)

    def post(self, url, data=None):
        json = data if data is not None else {}

        return requests.post(url, json=json, headers=self._headers)
