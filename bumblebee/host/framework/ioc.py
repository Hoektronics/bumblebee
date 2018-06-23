import inspect


class FailureToBindException(Exception):
    pass


def singleton(cls):
    Resolver._singleton_annotation(cls)

    return cls


class Resolver(object):
    _resolver_instance = None
    _annotated_singletons = []

    def __init__(self):
        self._bindings = {}

        self.instance(self)

    def __call__(self, cls):
        # Implicit binding
        if cls not in self._bindings:
            if cls in self._annotated_singletons:
                self.singleton(cls)
            else:
                self.bind(cls)

        return self._bindings[cls]()

    def _make(self, cls):
        args_spec = inspect.getfullargspec(cls.__init__)

        if len(args_spec.args) > 1:
            var_args = []

            for arg in args_spec.args[1:]:
                if arg in args_spec.annotations:
                    argument_class = args_spec.annotations[arg]
                    var_args.append(self.__call__(argument_class))
                else:
                    message = "Cannot bind argument {arg} for class {cls}".format(
                        arg=arg,
                        cls=cls
                    )
                    raise FailureToBindException(message)

            return cls(*var_args)

        return cls()

    def instance(self, cls, instance=None):
        if instance is None:
            if hasattr(cls, '__class__'):
                instance = cls
                cls = instance.__class__

        def _internal():
            return instance

        self._bindings[cls] = _internal

    def bind(self, cls):
        def _internal():
            return self._make(cls)

        self._bindings[cls] = _internal

    @classmethod
    def _singleton_annotation(cls, singleton_cls):
        cls._annotated_singletons.append(singleton_cls)

    def singleton(self, cls, resolving_function=None):
        def _internal():
            # instance is set on the _internal function as opposed to a class level dictionary
            # so that if we ever re-bind or clear the binding of a singleton class, the existing
            # instance is automatically cleared

            if not hasattr(_internal, 'instance'):
                if resolving_function is None:
                    _internal.instance = self._make(cls)
                else:
                    _internal.instance = resolving_function()

            return _internal.instance

        self._bindings[cls] = _internal

    def clear(self, cls=None):
        if cls is None:
            for key in list(self._bindings.keys()):
                del self._bindings[key]

        elif cls in self._bindings:
            del self._bindings[cls]

    @classmethod
    def get(cls):
        if cls._resolver_instance is None:
            cls._resolver_instance = Resolver()

        return cls._resolver_instance

    @classmethod
    def reset(cls):
        cls._resolver_instance = None
