from bumblebee.host.framework.events import EventBag, Event


class HostEvents(EventBag):
    class Startup(Event):
        pass

    class Shutdown(Event):
        pass
