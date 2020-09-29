from unittest.mock import Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.get_a_job import GetAJob
from bumblebee.host.events import JobEvents


class TestGetAJob(object):
    def test_get_job(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobStarted)

        api = Mock(BotQueueApi)
        resolver.instance(api)

        get_a_job = resolver(GetAJob)

        get_a_job(1)

        api.command.assert_called_with("GetAJob", {
            "bot": 1
        })
