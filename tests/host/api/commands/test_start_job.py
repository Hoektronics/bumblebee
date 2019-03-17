from unittest.mock import Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.start_job import StartJob
from bumblebee.host.events import JobEvents


class TestStartJob(object):
    def test_starting_job(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobStarted)

        api = Mock(BotQueueApi)
        api.command.return_value = {
            "id": 1,
            "name": "My Job",
            "status": "in_progress",
            "url": "file_url"
        }
        resolver.instance(api)

        start_job = resolver(StartJob)

        start_job(1)

        api.command.assert_called_with("StartJob", {
            "id": 1
        })

        assert fakes_events.fired(JobEvents.JobStarted).once()

        event: JobEvents.JobStarted = fakes_events.fired(JobEvents.JobStarted).event
        assert event.job.id == 1
        assert event.job.name == "My Job"
        assert event.job.status == "in_progress"
        assert event.job.file_url == "file_url"
