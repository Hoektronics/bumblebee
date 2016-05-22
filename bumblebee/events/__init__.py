class Event(object):
    @classmethod
    def then(cls, fn):
        _instance.on(cls, fn)

    def fire(self):
        _instance.fire(self)


class EventManager(object):
    def __init__(self):
        self.events = {}

    def fire(self, event):
        cls = event.__class__
        print "firing:", cls
        if cls in self.events:
            for fn in self.events[cls]:
                fn(event)

    def on(self, event_class, fn):
        if event_class not in self.events:
            self.events[event_class] = []

        self.events[event_class].append(fn)


_instance = EventManager()
