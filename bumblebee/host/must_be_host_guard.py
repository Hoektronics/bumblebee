import time

from bumblebee.host.api.commands.convert_request_to_host import ConvertRequestToHost
from bumblebee.host.api.commands.refresh_access_token import RefreshAccessToken
from bumblebee.host.api.commands.create_host_request import CreateHostRequest
from bumblebee.host.api.commands.get_host_request import GetHostRequest
from bumblebee.host.api.server import Server
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import ServerDiscovery
from bumblebee.host.framework.ioc import Resolver
from bumblebee.host.framework.events import on, bind_events
from bumblebee.host.managers.server_discovery_manager import ServerDiscoveryManager


@bind_events
class MustBeHostGuard(object):
    def __init__(self,
                 resolver: Resolver,
                 config: HostConfiguration,
                 server_discovery_manager: ServerDiscoveryManager):
        self._resolver = resolver
        self.config = config
        self._loop_wait = 10
        self._server_discovery_manager = server_discovery_manager

    def __call__(self):
        if "server" in self.config:
            server_url = self.config["server"]
            server = self._resolver(Server, url=server_url)
            self._resolver.instance(server)

            host_refresh: RefreshAccessToken = self._resolver(RefreshAccessToken)

            host_refresh()

            return

        # self._server_discovery_manager.start()

        # while True:
        #     time.sleep(10)

        while True:
            for server_url in self.config["servers"].keys():
                server = self._resolver(Server, url=server_url)
                get_host_request: GetHostRequest = self._resolver(GetHostRequest, server)
                response = get_host_request()

                if response["status"] == "claimed":
                    convert_to_host_request: ConvertRequestToHost = self._resolver(ConvertRequestToHost, server)
                    convert_to_host_request()
                    self._resolver.instance(server)

                    return

            time.sleep(self._loop_wait)

    @on(ServerDiscovery.ServerDiscovered)
    def _server_discovered(self, event: ServerDiscovery.ServerDiscovered):
        server = self._resolver(Server, url=event.url)

        create_host_request: CreateHostRequest = self._resolver(CreateHostRequest, server)

        create_host_request()
