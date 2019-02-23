from bumblebee.host.events import BotEvents, JobEvents
from bumblebee.host.framework.events import bind_events, on
from bumblebee.host.types import Bot


@bind_events
class JobsHandler(object):
    def __init__(self):
        self._jobs = {}

    @on(BotEvents.BotAdded)
    def _bot_added(self, event: BotEvents.BotAdded):
        bot = event.bot
        self._handle_job_assignment(bot)

    @on(BotEvents.BotUpdated)
    def _bot_updated(self, event: BotEvents.BotUpdated):
        bot = event.bot
        self._handle_job_assignment(bot)

    def _handle_job_assignment(self, bot: Bot):
        if bot.current_job is None:
            return

        job = bot.current_job
        job_id = job.id

        if job_id not in self._jobs and job.status == 'assigned':
            self._jobs[job_id] = job
            JobEvents.JobAssigned(job, bot).fire()
