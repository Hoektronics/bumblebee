from bumblebee.host.api.handlers.jobs import JobsHandler
from bumblebee.host.events import JobEvents, BotEvents
from bumblebee.host.types import Bot, Job


class TestJobsHandler(object):
    def test_job_is_not_assigned_if_not_in_creation_payload(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = Bot(
            id=1,
            name="Test bot",
            type="3d_printer",
            status="job_assigned"
        )
        BotEvents.BotAdded(bot).fire()

        assert not fakes_events.fired(JobEvents.JobAssigned)

    def test_job_is_not_assigned_if_not_in_update_payload(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = Bot(
            id=1,
            name="Test bot",
            type="3d_printer",
            status="job_assigned"
        )
        BotEvents.BotAdded(bot).fire()
        BotEvents.BotUpdated(bot).fire()

        assert not fakes_events.fired(JobEvents.JobAssigned)

    def test_job_is_assigned_on_bot_creation(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = Bot(
            id=1,
            name="Test bot",
            type="3d_printer",
            status="job_assigned",
            current_job=Job(
                id=1,
                name="Test Job",
                status="assigned",
                file_url="url"
            )
        )
        BotEvents.BotAdded(bot).fire()

        assert fakes_events.fired(JobEvents.JobAssigned).once()

    def test_job_is_assigned_on_bot_update(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = Bot(
            id=1,
            name="Test bot",
            type="3d_printer",
            status="job_assigned"
        )
        BotEvents.BotAdded(bot)

        assert not fakes_events.fired(JobEvents.JobAssigned)

        job = Job(
            id=1,
            name="Test Job",
            status="assigned",
            file_url="url"
        )
        bot.current_job = job
        BotEvents.BotUpdated(bot).fire()

        assert fakes_events.fired(JobEvents.JobAssigned).once()

    def test_job_is_assigned_once(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = Bot(
            id=1,
            name="Test bot",
            type="3d_printer",
            status="job_assigned",
            current_job=Job(
                id=1,
                name="Test Job",
                status="assigned",
                file_url="url"
            )
        )
        BotEvents.BotAdded(bot).fire()
        BotEvents.BotUpdated(bot).fire()

        assert fakes_events.fired(JobEvents.JobAssigned).once()
