from bumblebee.host.api.botqueue_api import BotQueueApi


class UpdateJobProgress(object):
    def __init__(self,
                 api: BotQueueApi):
        self.api = api

    def __call__(self, job_id, percentage):
        self.api.command("UpdateJobProgress", {
            "id": job_id,
            "progress": percentage
        })
