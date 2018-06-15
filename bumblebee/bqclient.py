from appdirs import AppDirs

from bumblebee.host import Host
from bumblebee.host import on
from bumblebee.host.events import HostEvents
from bumblebee.host.events import BotEvents
from bumblebee.host.framework import resolver


class BQClient(Host):
    app_name = 'BQClient'
    app_dirs = AppDirs(app_name)
    resolver.instance(app_dirs)

    def __init__(self):
        super(BQClient, self).__init__()

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
