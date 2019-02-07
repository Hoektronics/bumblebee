from bumblebee.host.api.handlers.jobs import JobsHandler
from bumblebee.host.events import JobEvents, BotEvents


class TestJobsHandler(object):
    def test_job_is_not_assigned_if_not_in_creation_payload(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "job_assigned"}
        BotEvents.BotAdded(bot).fire()

        assert not fakes_events.fired(JobEvents.JobAssigned)

    def test_job_is_not_assigned_if_not_in_update_payload(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "job_assigned"}
        BotEvents.BotAdded(bot).fire()
        BotEvents.BotUpdated(bot).fire()

        assert not fakes_events.fired(JobEvents.JobAssigned)

    def test_job_is_assigned_on_bot_creation(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        job = {"id": 1, "status": "assigned"}
        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "job_assigned", "job": job}
        BotEvents.BotAdded(bot).fire()

        assert fakes_events.fired(JobEvents.JobAssigned).once()

    def test_job_is_assigned_on_bot_update(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "job_assigned"}
        BotEvents.BotAdded(bot)

        assert not fakes_events.fired(JobEvents.JobAssigned)

        job = {"id": 1, "status": "assigned"}
        bot["job"] = job
        BotEvents.BotUpdated(bot).fire()

        assert fakes_events.fired(JobEvents.JobAssigned).once()

    def test_job_is_assigned_once(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobAssigned)

        resolver(JobsHandler)

        job = {"id": 1, "status": "assigned"}
        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "job_assigned", "job": job}
        BotEvents.BotAdded(bot).fire()
        BotEvents.BotUpdated(bot).fire()

        assert fakes_events.fired(JobEvents.JobAssigned).once()
