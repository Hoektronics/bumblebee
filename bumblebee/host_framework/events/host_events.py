from event import Event, EventBag


class HostEvents(EventBag):
    class Startup(Event):
        pass

    class Shutdown(Event):
        pass
