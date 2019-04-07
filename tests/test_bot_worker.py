from unittest.mock import MagicMock, Mock, call

import pytest

from bumblebee.bot_worker import BotWorker
from bumblebee.host.api.commands.finish_job import FinishJob
from bumblebee.host.api.commands.start_job import StartJob
from bumblebee.host.downloader import Downloader
from bumblebee.host.drivers.driver_factory import DriverFactory
from bumblebee.host.drivers.dummy import DummyDriver
from bumblebee.host.drivers.printrun import PrintrunDriver
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

        downloader.download.assert_called_once_with(job.file_url)
        start_job.assert_called_once_with(job.id)
        dummy_driver.run.assert_called_once_with("foo.gcode",
                                                 update_job_progress=worker._update_job_progress)
        finish_job.assert_called_once_with(job.id)

        dummy_driver.disconnect.assert_called_once()

    def test_bot_updated_does_not_force_driver_reconnect(self, resolver):
        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        driver_config = {
            "type": "gcode",
            "config": {
                "connection": {
                    "port": "test-port",
                    "baud": 115200
                }
            }
        }
        bot = Bot(
            id=1,
            name="Test Bot",
            status="job_assigned",
            type="3d_printer",
            driver=driver_config
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)

        bot.status = "working"

        BotEvents.BotUpdated(bot).fire()

        worker.stop()

        driver_factory.get.assert_called_once_with(driver_config)

    def test_bot_updated_calls_disconnect_first_if_driver_changes(self, resolver):
        driver_factory = MagicMock(DriverFactory)
        resolver.instance(driver_factory)

        driver_config_with_slow_baudrate = {
            "type": "gcode",
            "config": {
                "connection": {
                    "port": "test-port",
                    "baud": 115200
                }
            }
        }

        driver_config_with_fast_baudrate = {
            "type": "gcode",
            "config": {
                "connection": {
                    "port": "test-port",
                    "baud": 250000
                }
            }
        }

        gcode_driver_slow = Mock(PrintrunDriver)
        resolver.instance(gcode_driver_slow)
        gcode_driver_fast = Mock(PrintrunDriver)
        resolver.instance(gcode_driver_fast)

        manager = Mock()
        manager.attach_mock(gcode_driver_slow, 'slow')
        manager.attach_mock(gcode_driver_fast, 'fast')

        def return_correct_driver(config):
            if config == driver_config_with_slow_baudrate:
                return gcode_driver_slow
            if config == driver_config_with_fast_baudrate:
                return gcode_driver_fast
            pytest.fail(f"Bad config passed for getting the driver: {config}")

        driver_factory.get.side_effect = return_correct_driver

        bot = Bot(
            id=1,
            name="Test Bot",
            status="job_assigned",
            type="3d_printer",
            driver=driver_config_with_slow_baudrate
        )

        worker: BotWorker = resolver(BotWorker, bot=bot)

        new_bot = Bot(
            id=1,
            name="Test Bot",
            status="job_assigned",
            type="3d_printer",
            driver=driver_config_with_fast_baudrate
        )

        BotEvents.BotUpdated(new_bot).fire()

        worker.stop()

        manager.assert_has_calls([
            call.slow.connect(),
            call.slow.disconnect(),
            call.fast.connect(),
            call.fast.disconnect(),
        ])