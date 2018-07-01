import time

from bumblebee.host.api.commands.host_access import HostAccess
from bumblebee.host.api.commands.host_refresh import HostRefresh
from bumblebee.host.api.commands.make_host_request import MakeHostRequest
from bumblebee.host.api.queries.show_host_request import ShowHostRequest
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
            host_refresh: HostRefresh = resolver(HostRefresh)

            host_refresh()

            return

        make_host_request: MakeHostRequest = resolver(MakeHostRequest)

        make_host_request()

        show_host_request: ShowHostRequest = resolver(ShowHostRequest)
        while True:
            response = show_host_request()

            if response["status"] == "claimed":
                host_access: HostAccess = resolver(HostAccess)

                host_access()
                return

            time.sleep(self._loop_wait)