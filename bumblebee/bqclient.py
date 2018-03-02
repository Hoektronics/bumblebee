from __future__ import print_function

from appdirs import AppDirs

from .host_framework import Host
from .host_framework import on
from .host_framework.events import HostEvents
from .host_framework.events import BotEvents


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

    @on(BotEvents.BotAdded)
    def _bot_added(self, event):
        print("Bot added!")
        print(event.bot)

    @on(BotEvents.BotRemoved)
    def _bot_removed(self, event):
        print("Bot removed! :(")
        print(event.bot)
