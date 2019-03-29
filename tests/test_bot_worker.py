import json
from unittest.mock import Mock, MagicMock

import pytest

from bumblebee.bot_worker import BotWorker
from bumblebee.host.api.commands.finish_job import FinishJob
from bumblebee.host.api.commands.start_job import StartJob
from bumblebee.host.downloader import Downloader
from bumblebee.host.drivers.driver_factory import DriverFactory
from bumblebee.host.drivers.dummy import DummyDriver
from bumblebee.host.events import JobEvents, BotEvents
from bumblebee.host.types import Bot, Job


class TestBotWorker(object):
    def test_bot_worker_without_job_does_not_fire_job_assigned_event(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        bot = Bot(
            id=1,
            name="Test Bot",
            status="idle",
            type="3d_printer"
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)
        worker.stop()

        driver_factory.get.assert_not_called()
        assert not fakes_events.fired(JobEvents.JobAssigned)

    def test_bot_worker_with_job_fires_job_assigned_event(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        bot = Bot(
            id=1,
            name="Test Bot",
            status="job_assigned",
            type="3d_printer",
            current_job=Job(
                id=2,
                name="Test Job",
                status="assigned",
                file_url="http://foo/bar"
            )
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)
        worker.stop()

        driver_factory.get.assert_not_called()
        assert fakes_events.fired(JobEvents.JobAssigned).once()

    def test_bot_updated_event_fires_job_assigned_event(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        bot = Bot(
            id=1,
            name="Test Bot",
            status="job_assigned",
            type="3d_printer"
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)

        assert not fakes_events.fired(JobEvents.JobAssigned)

        bot.current_job = Job(
            id=2,
            name="Test Job",
            status="assigned",
            file_url="http://foo/bar"
        )

        BotEvents.BotUpdated(bot).fire()

        worker.stop()

        driver_factory.get.assert_not_called()
        assert fakes_events.fired(JobEvents.JobAssigned).once()

    def test_job_assigned_event_with_mismatched_job_id_does_nothing(self, resolver):
        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        bot_for_worker = Bot(
            id=1,
            name="Test Bot",
            status="idle",
            type="3d_printer"
        )

        worker: BotWorker = resolver(BotWorker, bot=bot_for_worker)

        job = Job(
            id=2,
            name="Test Job",
            status="assigned",
            file_url="http://foo/bar"
        )

        bot_for_job = Bot(
            id=2,
            name="Another Test Bot",
            status="job_assigned",
            type="3d_printer",
            current_job=job
        )

        JobEvents.JobAssigned(job, bot_for_job).fire()

        worker.stop()

        driver_factory.get.assert_not_called()

    def test_bot_with_driver_calls_connect(self, resolver):
        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        dummy_driver = MagicMock(DummyDriver)
        driver_factory.get.return_value = dummy_driver

        driver_config = {"type": "dummy"}
        bot = Bot(
            id=1,
            name="Test Bot",
            status="idle",
            type="3d_printer",
            driver=driver_config
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)
        worker.stop()

        driver_factory.get.assert_called_once_with(driver_config)
        dummy_driver.connect.assert_called_once()

    def test_bot_updated_to_add_driver_calls_connect(self, resolver):
        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        dummy_driver = MagicMock(DummyDriver)
        driver_factory.get.return_value = dummy_driver

        bot = Bot(
            id=1,
            name="Test Bot",
            status="idle",
            type="3d_printer"
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)

        driver_factory.get.assert_not_called()

        driver_config = {"type": "dummy"}
        bot.driver = driver_config

        BotEvents.BotUpdated(bot).fire()

        worker.stop()

        driver_factory.get.assert_called_once_with(driver_config)
        dummy_driver.connect.assert_called_once()

    def test_stopping_worker_calls_disconnect(self, resolver):
        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        dummy_driver = MagicMock(DummyDriver)
        driver_factory.get.return_value = dummy_driver

        driver_config = {"type": "dummy"}
        bot = Bot(
            id=1,
            name="Test Bot",
            status="idle",
            type="3d_printer",
            driver=driver_config
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)

        driver_factory.get.assert_called_once_with(driver_config)
        dummy_driver.connect.assert_called_once()
        dummy_driver.disconnect.assert_not_called()

        worker.stop()

        dummy_driver.disconnect.assert_called_once()

    def test_job_assigned_runs_through_job(self, resolver):
        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        dummy_driver = MagicMock(DummyDriver)
        driver_factory.get.return_value = dummy_driver

        driver_config = {"type": "dummy"}
        bot = Bot(
            id=1,
            name="Test Bot",
            status="job_assigned",
            type="3d_printer",
            driver=driver_config
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)

        driver_factory.get.assert_called_once_with(driver_config)
        dummy_driver.connect.assert_called_once()
        dummy_driver.disconnect.assert_not_called()

        job = Job(
            id=2,
            name="Test Job",
            status="assigned",
            file_url="https://test.url/foo.gcode"
        )

        downloader = MagicMock(Downloader)
        downloader.download.return_value = "foo.gcode"
        resolver.instance(downloader)

        start_job = MagicMock(StartJob)
        resolver.instance(start_job)

        finish_job = MagicMock(FinishJob)
        resolver.instance(finish_job)

        job_assigned: JobEvents.JobAssigned = JobEvents.JobAssigned(job, bot)
        job_assigned.fire()

        # TODO: Fix fragile test
        assert worker._current_job is not None
        while worker._current_job is not None:
            pass

        worker.stop()

        start_job.assert_called_once_with(job.id)
        downloader.download.assert_called_once_with(job.file_url)
        finish_job.assert_called_once_with(job.id)

        dummy_driver.disconnect.assert_called_once()
