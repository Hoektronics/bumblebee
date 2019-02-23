from bumblebee.host.framework.events import Event, EventBag
from bumblebee.host.types import HostRequest, Host, Bot, Job


class AuthFlowEvents(EventBag):
    class HostRequestMade(Event):
        def __init__(self, host_request: HostRequest):
            self.host_request = host_request

    class HostMade(Event):
        def __init__(self, host: Host):
            self.host = host


class BotEvents(EventBag):
    class BotAdded(Event):
        def __init__(self, bot: Bot):
            self.bot = bot

    class BotRemoved(Event):
        def __init__(self, bot: Bot):
            self.bot = bot

    class BotUpdated(Event):
        def __init__(self, bot: Bot):
            self.bot = bot


class JobEvents(EventBag):
    class JobAssigned(Event):
        def __init__(self, job: Job, bot: Bot):
            self.job = job
            self.bot = bot

    class JobStarted(Event):
        def __init__(self, job: Job):
            self.job = job

    class JobFinished(Event):
        def __init__(self, job: Job):
            self.job = job


class HostEvents(EventBag):
    class Startup(Event):
        pass

    class Shutdown(Event):
        pass
