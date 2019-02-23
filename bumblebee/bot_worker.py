from threading import Thread

from bumblebee.host import on
from bumblebee.host.api.commands.finish_job import FinishJob
from bumblebee.host.api.commands.start_job import StartJob
from bumblebee.host.downloader import Downloader
from bumblebee.host.drivers.dummy import DummyDriver
from bumblebee.host.drivers.printrun import PrintrunDriver
from bumblebee.host.events import JobEvents
from bumblebee.host.framework.events import bind_events
from bumblebee.host.framework.ioc import Resolver


@bind_events
class BotWorker(object):
    def __init__(self, bot_id,
                 resolver: Resolver):
        self.bot_id = bot_id
        self.resolver = resolver
        self.thread = None

    @on(JobEvents.JobAssigned)
    def job_assigned(self, event: JobEvents.JobAssigned):
        if self.bot_id != event.bot.id:
            return

        url = event.job["url"]

        downloader = self.resolver(Downloader)
        print(f"Downloading {url}")
        filename = downloader.download(url)
        print("Downloaded")
        dummy_driver = PrintrunDriver()

        job_execution = JobExecution(event.job.id, filename, dummy_driver, self.resolver)

        self.thread = Thread(target=job_execution.run)
        self.thread.start()


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