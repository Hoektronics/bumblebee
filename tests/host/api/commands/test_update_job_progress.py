from unittest.mock import Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.update_job_progress import UpdateJobProgress


class TestUpdateJobProgress(object):
    def test_updating_job_progress_calls_correct_command(self, resolver):
        api = Mock(BotQueueApi)
        api.command.return_value = {
            "id": 1,
            "name": "My Job",
            "status": "in_progress",
            "progress": 50.0,
            "url": "file_url"
        }
        resolver.instance(api)

        update_job_progress = resolver(UpdateJobProgress)

        update_job_progress(1, 50.0)

        api.command.assert_called_with("UpdateJobProgress", {
            "id": 1,
            "progress": 50.0
        })
