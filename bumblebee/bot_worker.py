import json
import time
from threading import Thread, Event

from bumblebee.host import on
from bumblebee.host.api.commands.finish_job import FinishJob
from bumblebee.host.api.commands.start_job import StartJob
from bumblebee.host.downloader import Downloader
from bumblebee.host.drivers.driver_factory import DriverFactory
from bumblebee.host.events import JobEvents, BotEvents
from bumblebee.host.framework.events import bind_events, EventManager
from bumblebee.host.framework.ioc import Resolver
from bumblebee.host.types import Bot, Job


def _handle_job_assignment(bot: Bot):
    if bot.current_job is None:
        return

    job = bot.current_job

    if job.status == 'assigned':
        JobEvents.JobAssigned(job, bot).fire()


class BotWorker(object):
    def __init__(self,
                 bot: Bot,
                 resolver: Resolver, ):
        self.bot = bot
        self.resolver = resolver

        self.driver_config = None
        self.driver = None
        self._handle_driver()

        self._current_job: Job = None
        self._thread = Thread(target=self._run, daemon=True)
        self._worker_should_be_stopped = Event()
        self._thread.start()

    def stop(self):
        self._worker_should_be_stopped.set()
        self._thread.join(1)
        if self.driver is not None:
            self.driver.disconnect()

    def _handle_driver(self):
        if self.bot.driver is not None:
            if self.driver_config == self.bot.driver:
                return
            else:
                self.driver_config = self.bot.driver

                if self.driver is not None:
                    self.driver.disconnect()

            self.driver = self.resolver(DriverFactory).get(self.driver_config)
            self.driver.connect()

    @on(BotEvents.BotUpdated)
    def _bot_updated(self, event: BotEvents.BotUpdated):
        self.bot = event.bot
        self._handle_driver()
        _handle_job_assignment(self.bot)

    @on(JobEvents.JobAssigned)
    def job_assigned(self, event: JobEvents.JobAssigned):
        if self.bot.id != event.bot.id:
            return

        self._current_job = event.job

    def _run(self):
        # Bind manually, otherwise JobAssigned won't be bound to this
        # instance when we need it in the _handle_job_assignment call
        event_manager = self.resolver(EventManager)
        event_manager.bind(self)

        _handle_job_assignment(self.bot)

        while not self._worker_should_be_stopped.is_set():
            if self._current_job is not None:
                url = self._current_job.file_url

                downloader = self.resolver(Downloader)
                print(f"Downloading {url}")
                filename = downloader.download(url)
                print("Downloaded")

                start_job_command = self.resolver(StartJob)
                start_job_command(self._current_job.id)

                self.driver.run(filename)

                finish_job_command = self.resolver(FinishJob)
                finish_job_command(self._current_job.id)

                self._current_job = None
            else:
                time.sleep(0.05)