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
            driver={
                "type": "dummy"
            },
            current_job=Job(
                id=2,
                name="Test Job",
                status="assigned",
                file_url="url"
            )
        )
        BotEvents.BotAdded(bot).fire()

        job_assigned_event_assertion = fakes_events.fired(JobEvents.JobAssigned)
        assert job_assigned_event_assertion.once()

        event: JobEvents.JobAssigned = job_assigned_event_assertion.event
        assert event.bot.id == 1
        assert event.bot.name == "Test bot"
        assert event.bot.status == "job_assigned"
        assert event.bot.type == "3d_printer"
        assert event.bot.driver == {"type": "dummy"}
        assert event.bot.current_job.id == 2
        assert event.bot.current_job.name == "Test Job"
        assert event.bot.current_job.status == "assigned"
        assert event.bot.current_job.file_url == "url"
        assert event.job.id == 2
        assert event.job.name == "Test Job"
        assert event.job.status == "assigned"
        assert event.job.file_url == "url"

    def test_job_is_assigned_on_bot_update(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = Bot(
            id=1,
            name="Test bot",
            type="3d_printer",
            status="job_assigned",
            driver={
                "type": "dummy"
            }
        )
        BotEvents.BotAdded(bot)

        assert not fakes_events.fired(JobEvents.JobAssigned)

        job = Job(
            id=2,
            name="Test Job",
            status="assigned",
            file_url="url"
        )
        bot.current_job = job
        BotEvents.BotUpdated(bot).fire()

        job_assigned_event_assertion = fakes_events.fired(JobEvents.JobAssigned)
        assert job_assigned_event_assertion.once()

        event: JobEvents.JobAssigned = job_assigned_event_assertion.event
        assert event.bot.id == 1
        assert event.bot.name == "Test bot"
        assert event.bot.status == "job_assigned"
        assert event.bot.type == "3d_printer"
        assert event.bot.driver == {"type": "dummy"}
        assert event.bot.current_job.id == 2
        assert event.bot.current_job.name == "Test Job"
        assert event.bot.current_job.status == "assigned"
        assert event.bot.current_job.file_url == "url"
        assert event.job.id == 2
        assert event.job.name == "Test Job"
        assert event.job.status == "assigned"
        assert event.job.file_url == "url"

    def test_job_is_assigned_once(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = Bot(
            id=1,
            name="Test bot",
            type="3d_printer",
            status="job_assigned",
            driver={
                "type": "dummy"
            },
            current_job=Job(
                id=2,
                name="Test Job",
                status="assigned",
                file_url="url"
            )
        )
        BotEvents.BotAdded(bot).fire()
        BotEvents.BotUpdated(bot).fire()

        job_assigned_event_assertion = fakes_events.fired(JobEvents.JobAssigned)
        assert job_assigned_event_assertion.once()

        event: JobEvents.JobAssigned = job_assigned_event_assertion.event
        assert event.bot.id == 1
        assert event.bot.name == "Test bot"
        assert event.bot.status == "job_assigned"
        assert event.bot.type == "3d_printer"
        assert event.bot.driver == {"type": "dummy"}
        assert event.bot.current_job.id == 2
        assert event.bot.current_job.name == "Test Job"
        assert event.bot.current_job.status == "assigned"
        assert event.bot.current_job.file_url == "url"
        assert event.job.id == 2
        assert event.job.name == "Test Job"
        assert event.job.status == "assigned"
        assert event.job.file_url == "url"
