from typing import List

from deepdiff import DeepDiff

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.events import BotEvents
from bumblebee.host.framework.recurring_task import RecurringTask
from bumblebee.host.types import Job, Bot


class BotsManager(object):
    def __init__(self,
                 api: BotQueueApi):
        self.api = api

        self._bots = {}
        self._polling_thread = RecurringTask(60, self.poll)

    def start(self):
        self._polling_thread.start()

    def poll(self):
        response = self.api.command("GetBots")

        _bot_ids_seen_in_response = []
        for bot_json in response:
            job = None
            if "job" in bot_json and bot_json["job"] is not None:
                job = Job(
                    id=bot_json["job"]["id"],
                    name=bot_json["job"]["name"],
                    status=bot_json["job"]["status"],
                    file_url=bot_json["job"]["url"]
                )

            bot = Bot(
                id=bot_json["id"],
                name=bot_json["name"],
                status=bot_json["status"],
                type=bot_json["type"],
                driver=bot_json["driver"],
                current_job=job,
                job_available=bot_json["job_available"]
            )

            if bot.id not in self._bots:
                BotEvents.BotAdded(bot).fire()
            else:
                diff = DeepDiff(self._bots[bot.id], bot)
                if diff:
                    BotEvents.BotUpdated(bot).fire()

            _bot_ids_seen_in_response.append(bot.id)
            self._bots[bot.id] = bot

        for bot_id in list(self._bots.keys()):
            if bot_id not in _bot_ids_seen_in_response:
                BotEvents.BotRemoved(self._bots[bot_id]).fire()
                del self._bots[bot_id]
