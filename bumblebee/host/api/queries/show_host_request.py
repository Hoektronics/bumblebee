from requests import Response

from bumblebee.host.api.rest import RestApi
from bumblebee.host.configurations import HostConfiguration


class ShowHostRequest(object):
    def __init__(self,
                 config: HostConfiguration,
                 api: RestApi):
        self.config = config
        self.api = api

    def __call__(self):
        request_id = self.config["host_request_id"]
        response: Response = self.api.get(f"/host/requests/{request_id}")

        if response.ok:
            json = response.json()
            return json['data']
