import time

from bumblebee.host.api.commands.convert_request_to_host import ConvertRequestToHost
from bumblebee.host.api.commands.refresh_access_token import RefreshAccessToken
from bumblebee.host.api.commands.create_host_request import CreateHostRequest
from bumblebee.host.api.queries.get_host_request import GetHostRequest
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.framework.ioc import Resolver


class MustBeHostGuard(object):
    def __init__(self,
                 config: HostConfiguration):
        self.config = config
        self._loop_wait = 10

    def __call__(self):
        resolver = Resolver.get()

        if "access_token" in self.config:
            host_refresh: RefreshAccessToken = resolver(RefreshAccessToken)

            host_refresh()

            return

        make_host_request: CreateHostRequest = resolver(CreateHostRequest)

        make_host_request()

        show_host_request: GetHostRequest = resolver(GetHostRequest)
        while True:
            response = show_host_request()

            if response["status"] == "claimed":
                host_access: ConvertRequestToHost = resolver(ConvertRequestToHost)

                host_access()
                return

            time.sleep(self._loop_wait)