from __future__ import print_function

from appdirs import AppDirs

from .host_framework import Host
from .host_framework import on
from .host_framework.events import HostEvents
from .host_framework.events import AuthFlowEvents


class BQClient(Host):
    app_name = 'BQClient'
    app_dirs = AppDirs(app_name)

    def __init__(self):
        super(BQClient, self).__init__(self.app_dirs)

    @on(HostEvents.Startup)
    def _start(self):
        print("Host startup!")

    @on(HostEvents.Shutdown)
    def _shutdown(self):
        print("Host shutdown!")

    @on(AuthFlowEvents.HostRequestMade)
    def _host_request_made(self, event):
        print(event.host_request)

    @on(AuthFlowEvents.HostMade)
    def _host_made(self, event):
        print(event.host)