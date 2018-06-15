import inspect


class Event(object):
    def fire(self):
        event_manager.fire(self)


class EventBag(object):
    pass


class EventManager(object):
    def __init__(self):
        self._listeners = {}
        self._unbound_methods = {}

    def on(self, event_class, callback):
        if event_class not in self._listeners:
            self._listeners[event_class] = []

        self._listeners[event_class].append(callback)

    def fire(self, event):
        if event.__class__ in self._listeners:
            for listener in self._listeners[event.__class__]:
                argspec = inspect.getargspec(listener)

                if len(argspec.args) == 1:
                    listener()
                else:
                    listener(event)

    def add_unbound_method(self, event_class, unbound_method):
        if unbound_method not in self._unbound_methods:
            self._unbound_methods[unbound_method] = []

        self._unbound_methods[unbound_method].append(event_class)

    def bind(self, obj):
        for obj_attribute_name in dir(obj):
            obj_attribute = getattr(obj, obj_attribute_name)

            if not hasattr(obj_attribute, '__func__'):
                continue

            unbound_function = getattr(obj_attribute, '__func__')

            if unbound_function in self._unbound_methods:
                for event_class in self._unbound_methods[unbound_function]:
                    self.on(event_class, obj_attribute)


event_manager = EventManager()


def on(event_class):
    def _on(unbound_method):
        event_manager.add_unbound_method(event_class, unbound_method)

        return unbound_method
    return _on
