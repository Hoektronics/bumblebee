import functools
import inspect


class Event(object):
    def fire(self):
        event_manager.fire(self)


class EventBag(object):
    pass


class EventManager(object):
    def __init__(self):
        self.listeners = {}

    def on(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []

        self.listeners[event].append(callback)

    def fire(self, event):
        if event in self.listeners:
            for listener in self.listeners[event]:
                listener(event)


event_manager = EventManager()


def on(event):
    def _on(method):
        @functools.wraps(method)
        def wrapper(self):
            argspec = inspect.getargspec(method)

            if len(argspec.args) == 1:
                return method(self)
            else:
                return method(self, event)

        event_manager.on(event, wrapper)

        return wrapper

    return _on
