from unittest.mock import MagicMock, PropertyMock

from requests import Response

from bumblebee.host.api.commands.finish_job import FinishJob
from bumblebee.host.api.rest import RestApi
from bumblebee.host.events import JobEvents


class TestFinishJob(object):
    def test_finishing_job(self, resolver, fakes_events):
        fakes_events.fake(JobEvents.JobFinished)

        job_start_response = MagicMock(Response)
        job_start_ok_mock = PropertyMock(return_value=True)
        type(job_start_response).ok = job_start_ok_mock
        job_start_response.json.return_value = {}

        job_show_response = MagicMock(Response)
        job_show_ok_mock = PropertyMock(return_value=True)
        type(job_show_response).ok = job_show_ok_mock
        job_show_response.json.return_value = {
            "id": 1,
            "name": "My Job",
            "status": "in_progress",
            "url": "file_url"
        }

        api = MagicMock(RestApi)
        api.with_token.return_value = api
        api.put.return_value = job_start_response
        api.get.return_value = job_show_response
        resolver.instance(api)

        start_job = resolver(FinishJob)

        start_job(1)

        api.put.assert_called_with("/host/jobs/1", {
            "status": "quality_check"
        })
        api.get.assert_called_with("/host/jobs/1")

        api.with_token.assert_called()
        job_start_ok_mock.assert_called()
        job_show_ok_mock.assert_called()
        job_show_response.json.assert_called()

        assert fakes_events.fired(JobEvents.JobFinished).once()

        event: JobEvents.JobFinished = fakes_events.fired(JobEvents.JobFinished).event
        assert event.job.id == 1
        assert event.job.name == "My Job"
        assert event.job.status == "in_progress"
        assert event.job.file_url == "file_url"
