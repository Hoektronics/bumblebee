import json
from threading import Thread

from bumblebee.host import on
from bumblebee.host.api.commands.finish_job import FinishJob
from bumblebee.host.api.commands.start_job import StartJob
from bumblebee.host.downloader import Downloader
from bumblebee.host.drivers.driver_factory import DriverFactory
from bumblebee.host.events import JobEvents, BotEvents
from bumblebee.host.framework.events import bind_events
from bumblebee.host.framework.ioc import Resolver
from bumblebee.host.types import Bot


def _handle_job_assignment(bot: Bot):
    if bot.current_job is None:
        return

    job = bot.current_job

    if job.status == 'assigned':
        JobEvents.JobAssigned(job, bot).fire()


@bind_events
class BotWorker(object):
    def __init__(self,
                 bot: Bot,
                 resolver: Resolver):
        self.bot = bot
        self.resolver = resolver

        self._current_job = None
        self._thread = None
        _handle_job_assignment(bot)

    @on(BotEvents.BotUpdated)
    def _bot_updated(self, event: BotEvents.BotUpdated):
        bot = event.bot
        _handle_job_assignment(bot)

    @on(JobEvents.JobAssigned)
    def job_assigned(self, event: JobEvents.JobAssigned):
        if self.bot.id != event.bot.id:
            return

        url = event.job.file_url

        downloader = self.resolver(Downloader)
        print(f"Downloading {url}")
        filename = downloader.download(url)
        print("Downloaded")

        driver_factory: DriverFactory = self.resolver(DriverFactory)
        driver = driver_factory.get(json.loads(event.bot.driver))

        job_execution = JobExecution(event.job.id, filename, driver, self.resolver)

        self._thread = Thread(target=job_execution.run)
        self._thread.start()


class JobExecution(object):
    def __init__(self, job_id, filename, driver, resolver):
        self.job_id = job_id
        self.filename = filename
        self.driver = driver
        self.resolver = resolver

    def run(self):
        start_job_command = self.resolver(StartJob)
        start_job_command(self.job_id)

        self.driver.run(self.filename)

        finish_job_command = self.resolver(FinishJob)
        finish_job_command(self.job_id)