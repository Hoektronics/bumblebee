from typing import List

from deepdiff import DeepDiff

from bumblebee.host.api.rest import RestApi
from bumblebee.host.events import BotEvents, JobEvents
from bumblebee.host.framework.api.handler import Handler
from bumblebee.host.framework.events import bind_events
from bumblebee.host.framework.recurring_task import RecurringTask


@bind_events
class BotsHandler(Handler):
    def __init__(self,
                 rest: RestApi):
        self.rest = rest

        self._bots = {}
        self._tasks = [
            RecurringTask(60, self.poll)
        ]

    def tasks(self) -> List[RecurringTask]:
        return self._tasks

    def poll(self):
        response = self.rest.with_token().get("/host/bots")

        if not response.ok:
            return

        json = response.json()

        _bot_ids_seen_in_response = []
        for bot in json["data"]:
            bot_id = bot["id"]

            if bot_id not in self._bots:
                BotEvents.BotAdded(bot).fire()
            else:
                diff = DeepDiff(self._bots[bot_id], bot)
                if diff:
                    BotEvents.BotUpdated(bot).fire()

            if "job" in bot:
                JobEvents.JobAssigned(bot["job"]).fire()

            _bot_ids_seen_in_response.append(bot_id)
            self._bots[bot_id] = bot

        for bot_id in list(self._bots.keys()):
            if bot_id not in _bot_ids_seen_in_response:
                BotEvents.BotRemoved(self._bots[bot_id]).fire()
                del self._bots[bot_id]
