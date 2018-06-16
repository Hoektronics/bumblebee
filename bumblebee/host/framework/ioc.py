import inspect


class FailureToBindException(Exception):
    pass


def singleton(resolver):
    def _singleton(cls):
        resolver.singleton(cls)

        return cls

    return _singleton


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
