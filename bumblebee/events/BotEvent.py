from bumblebee.events import Event


class Added(Event):
    def __init__(self, bot_data):
        self.data = bot_data


class Removed(Event):
    def __init__(self, bot_id):
        self.bot_id = bot_id


class Updated(Event):
    def __init__(self, bot_data):
        self.data = bot_data