import inspect


class FailureToBindException(Exception):
    pass


class Resolver(object):
    def __init__(self):
        self._bindings = {}

    def __call__(self, cls):
        # Implicit binding
        if cls not in self._bindings:
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

    def singleton(self, cls, resolving_function):
        def _internal():
            if not hasattr(_internal, 'singletons'):
                _internal.singletons = {}

            if cls not in _internal.singletons:
                _internal.singletons[cls] = resolving_function()

            return _internal.singletons[cls]

        self._bindings[cls] = _internal
