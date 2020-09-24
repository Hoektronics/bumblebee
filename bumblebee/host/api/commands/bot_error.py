import traceback

from bumblebee.host.api.botqueue_api import BotQueueApi


class BotError(object):
    def __init__(self,
                 api: BotQueueApi):
        self.api = api

    def __call__(self, bot_id, error):
        if isinstance(error, BaseException):
            error = ''.join(traceback.format_exception(None, error, error.__traceback__))

        self.api.command("BotError", {
            "id": bot_id,
            "error": error
        })
