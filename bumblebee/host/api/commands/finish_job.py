from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.events import JobEvents
from bumblebee.host.types import Job


class FinishJob(object):
    def __init__(self,
                 api: BotQueueApi):
        self.api = api

    def __call__(self, job_id):
        response = self.api.command("FinishJob", {
            "id": job_id
        })
        
        job = Job(
            id=response["id"],
            name=response["name"],
            status=response["status"],
            file_url=response["url"]
        )

        JobEvents.JobFinished(job).fire()