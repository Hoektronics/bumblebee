from bumblebee.host_framework.events.event import Event, EventBag


class BotEvents(EventBag):
    class BotAdded(Event):
        def __init__(self, bot):
            self.bot = bot

    class BotRemoved(Event):
        def __init__(self, bot):
            self.bot = bot
