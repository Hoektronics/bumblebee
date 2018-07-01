import inspect

from bumblebee.host.framework.ioc import singleton, Resolver


class Event(object):
    def fire(self):
        resolver = Resolver.get()
        event_manager = resolver(EventManager)
        event_manager.fire(self)


class EventBag(object):
    pass


class EventCallbackWrapper(object):
    def __init__(self, callback, event_spec):
        self.callback = callback
        self.event_spec = event_spec

    @property
    def event_class(self):
        if inspect.isclass(self.event_spec):
            return self.event_spec
        else:
            return self.event_spec.__class__

    def __call__(self, event: Event):
        arg_spec = inspect.getfullargspec(self.callback)

        args_length = len(arg_spec.args)

        # If it's a method, the first parameter is self
        if inspect.ismethod(self.callback):
            args_length = args_length - 1

        if args_length == 0:
            self.callback()
        else:
            self.callback(event)

@singleton
class EventManager(object):
    def __init__(self):
        self._listeners = {}
        self._unbound_methods = {}

    def on(self, event_spec, callback):
        wrapper = EventCallbackWrapper(callback, event_spec)
        event_class = wrapper.event_class

        if event_class not in self._listeners:
            self._listeners[event_class] = []

        self._listeners[event_class].append(wrapper)

    def fire(self, event):
        if event.__class__ in self._listeners:
            for listener in self._listeners[event.__class__]:
                listener(event)

    def add_unbound_method(self, event_spec, unbound_method):
        if unbound_method not in self._unbound_methods:
            self._unbound_methods[unbound_method] = []

        self._unbound_methods[unbound_method].append(event_spec)

    def bind(self, obj):
        for obj_attribute_name in dir(obj):
            obj_attribute = getattr(obj, obj_attribute_name)

            if not hasattr(obj_attribute, '__func__'):
                continue

            # This attribute is already bound, probably a class method
            if obj_attribute in self._unbound_methods:
                for event_spec in self._unbound_methods[obj_attribute]:
                    self.on(event_spec, obj_attribute)

            unbound_function = getattr(obj_attribute, '__func__')

            if unbound_function in self._unbound_methods:
                for event_spec in self._unbound_methods[unbound_function]:
                    self.on(event_spec, obj_attribute)


def on(event_spec):
    def _on(unbound_method):

        resolver = Resolver.get()
        resolver(EventManager).add_unbound_method(event_spec, unbound_method)

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
