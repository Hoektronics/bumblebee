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


class StatusChanged(Event):
    def __init__(self, old_status, new_status):
        self.old_status = old_status
        self.new_status = new_status
