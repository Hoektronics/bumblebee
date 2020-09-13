from bumblebee.host.framework.events import EventBag, Event


class ServerDiscovery(EventBag):
    class ServerDiscovered(Event):
        def __init__(self, url):
            self.url = url
