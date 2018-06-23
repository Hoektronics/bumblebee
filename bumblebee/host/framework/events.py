import inspect

from bumblebee.host.framework.ioc import singleton, Resolver


class Event(object):
    def fire(self):
        resolver = Resolver.get()
        event_manager = resolver(EventManager)
        event_manager.fire(self)


class EventBag(object):
    pass


@singleton
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
                arg_spec = inspect.getfullargspec(listener)

                args_length = len(arg_spec.args)

                # If it's a method, the first parameter is self
                if inspect.ismethod(listener):
                    args_length = args_length - 1

                if args_length == 0:
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

            # This attribute is already bound, probably a class method
            if obj_attribute in self._unbound_methods:
                for event_class in self._unbound_methods[obj_attribute]:
                    self.on(event_class, obj_attribute)

            unbound_function = getattr(obj_attribute, '__func__')

            if unbound_function in self._unbound_methods:
                for event_class in self._unbound_methods[unbound_function]:
                    self.on(event_class, obj_attribute)


def on(event_class):
    def _on(unbound_method):

        resolver = Resolver.get()
        resolver(EventManager).add_unbound_method(event_class, unbound_method)

        return unbound_method
    return _on


def bind_events(event_class):
    def _internal_init(*args, **kwargs):
        instance = event_class(*args, **kwargs)

        resolver = Resolver.get()
        resolver(EventManager).bind(instance)

        return instance

    # When the resolver sees this function, we want it to use the parameters from
    # the __init__ of the class we're annotating as opposed to *args and **kwargs
    _internal_init.__init__ = event_class.__init__

    return _internal_init
