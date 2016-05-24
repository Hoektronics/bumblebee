class Event(object):
    _events = {}

    @classmethod
    def then(cls, fn):
        if cls not in cls._events:
            Event._events[cls] = []

        Event._events[cls].append(fn)

    def fire(self):
        cls = self.__class__
        print "firing:", cls
        if cls in Event._events:
            for fn in Event._events[cls]:
                fn(self)
