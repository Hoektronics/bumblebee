from bumblebee.host.framework.events import Event, EventBag


class AuthFlowEvents(EventBag):
    class HostRequestMade(Event):
        def __init__(self, host_request):
            self.host_request = host_request

    class HostMade(Event):
        def __init__(self, host):
            self.host = host


class BotEvents(EventBag):
    class BotAdded(Event):
        def __init__(self, bot):
            self.bot = bot

    class BotRemoved(Event):
        def __init__(self, bot):
            self.bot = bot

    class BotUpdated(Event):
        def __init__(self, bot):
            self.bot = bot


class JobEvents(EventBag):
    class JobAssigned(Event):
        def __init__(self, job):
            self.job = job

    class JobStarted(Event):
        def __init__(self, job):
            self.job = job


class HostEvents(EventBag):
    class Startup(Event):
        pass

    class Shutdown(Event):
        pass
