from __future__ import print_function

from .host_framework import Host
from .host_framework import on
from .host_framework.events import HostEvents


class BQClient(Host):
    app_name = 'bqclient'

    def __init__(self):
        super(BQClient, self).__init__(self.app_name)

    @on(HostEvents.Startup)
    def _start(self):
        print("Host startup!")

    @on(HostEvents.Shutdown)
    def _shutdown(self):
        print("Host shutdown!")
