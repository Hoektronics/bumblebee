from bumblebee.host.framework.events import EventBag, Event
from bumblebee.host.types import Bot, Job


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
