from bumblebee.host.api.botqueue_api import BotQueueApi


class GetAJob(object):
    def __init__(self,
                 api: BotQueueApi):
        self.api = api

    def __call__(self, bot_id):
        self.api.command("GetAJob", {
            "bot": bot_id
        })
