import pytest

from bumblebee.host.framework.ioc import Resolver, FailureToBindException, singleton


class NoArgumentFakeClass(object):
    pass


class OneArgumentFakeClass(object):
    def __init__(self, foo: NoArgumentFakeClass):
        self.foo = foo


class UnannotatedFakeClass(object):
    def __init__(self, foo):
        self.foo = foo


class ClassWithResolver(object):
    def __init__(self, resolver: Resolver):
        self.resolver = resolver


class TestIocResolver(object):
    def test_can_resolve_given_instance(self, resolver):
        instance = NoArgumentFakeClass()

        resolver.instance(NoArgumentFakeClass, instance)

        fake_class = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class, NoArgumentFakeClass)
        assert fake_class is instance

    def test_can_resolve_given_only_instance(self, resolver):
        instance = NoArgumentFakeClass()

        resolver.instance(instance)

        fake_class = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class, NoArgumentFakeClass)
        assert fake_class is instance

    def test_can_resolve_explicitly_bound_class(self, resolver):
        resolver = Resolver()

        resolver.bind(NoArgumentFakeClass)

        fake_class = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class, NoArgumentFakeClass)

    def test_can_resolve_singleton_function(self, resolver):
        def resolve_instance():
            return NoArgumentFakeClass()

        resolver.singleton(NoArgumentFakeClass, resolve_instance)

        fake_class_first_time = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class_first_time, NoArgumentFakeClass)

        fake_class_second_time = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class_second_time, NoArgumentFakeClass)
        assert fake_class_second_time is fake_class_first_time

    def test_can_resolve_singleton_given_only_class(self, resolver):
        resolver.singleton(NoArgumentFakeClass)

        fake_class_first_time = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class_first_time, NoArgumentFakeClass)

        fake_class_second_time = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class_second_time, NoArgumentFakeClass)
        assert fake_class_second_time is fake_class_first_time

    def test_can_resolve_implicitly_bound_class(self, resolver):
        fake_class = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class, NoArgumentFakeClass)

    def test_can_resolve_chain_of_classes_based_on_type_hinting(self, resolver):
        fake_class: OneArgumentFakeClass = resolver(OneArgumentFakeClass)

        assert isinstance(fake_class, OneArgumentFakeClass)
        assert isinstance(fake_class.foo, NoArgumentFakeClass)

    def test_can_resolve_chain_using_instance(self, resolver):
        instance = NoArgumentFakeClass()

        resolver.instance(NoArgumentFakeClass, instance)

        fake_class: OneArgumentFakeClass = resolver(OneArgumentFakeClass)

        assert isinstance(fake_class, OneArgumentFakeClass)
        assert isinstance(fake_class.foo, NoArgumentFakeClass)
        assert fake_class.foo is instance

    def test_cannot_resolve_unannotated_parameters(self, resolver):
        with pytest.raises(FailureToBindException):
            resolver(UnannotatedFakeClass)

    def test_using_singleton_annotation(self, resolver):
        @singleton
        class SingletonClass(object):
            pass

        fake_class_first_time = resolver(SingletonClass)

        assert isinstance(fake_class_first_time, SingletonClass)

        fake_class_second_time = resolver(SingletonClass)

        assert isinstance(fake_class_second_time, SingletonClass)
        assert fake_class_second_time is fake_class_first_time

    def test_clearing_the_resolver_clears_bound_instances(self, resolver):
        instance = NoArgumentFakeClass()

        resolver.instance(NoArgumentFakeClass, instance)

        fake_class = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class, NoArgumentFakeClass)
        assert fake_class is instance

        resolver.clear(NoArgumentFakeClass)

        fake_class = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class, NoArgumentFakeClass)
        assert fake_class is not instance

    def test_clearing_the_resolver_clears_singleton_instance(self, resolver):
        resolver.singleton(NoArgumentFakeClass)

        fake_class_first_time = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class_first_time, NoArgumentFakeClass)

        resolver.clear(NoArgumentFakeClass)

        fake_class_second_time = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class_second_time, NoArgumentFakeClass)
        assert fake_class_second_time is not fake_class_first_time

    def test_clearing_a_class_that_was_not_bound_works(self, resolver):
        resolver.clear(NoArgumentFakeClass)

    def test_resetting_the_resolver_clears_bound_instances(self, resolver):
        instance = NoArgumentFakeClass()

        resolver.instance(NoArgumentFakeClass, instance)

        fake_class = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class, NoArgumentFakeClass)
        assert fake_class is instance

        resolver.clear()

        fake_class = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class, NoArgumentFakeClass)
        assert fake_class is not instance

    def test_resetting_the_resolver_clears_singleton_instance(self, resolver):
        resolver.singleton(NoArgumentFakeClass)

        fake_class_first_time = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class_first_time, NoArgumentFakeClass)

        resolver.clear()

        fake_class_second_time = resolver(NoArgumentFakeClass)

        assert isinstance(fake_class_second_time, NoArgumentFakeClass)
        assert fake_class_second_time is not fake_class_first_time

    def test_resolver_resolves_to_itself(self, resolver):
        class_with_resolver: ClassWithResolver = resolver(ClassWithResolver)

        assert class_with_resolver.resolver is resolver

    def test_getting_the_resolver_instance(self):
        first = Resolver.get()

        second = Resolver.get()

        assert isinstance(first, Resolver)
        assert first is second

    def test_resetting_the_resolver_instance(self):
        first = Resolver.get()

        Resolver.reset()

        second = Resolver.get()

        assert isinstance(first, Resolver)
        assert isinstance(second, Resolver)
        assert first is not second

    def test_resetting_keeps_decorated_singletons_as_singletons(self):
        resolver = Resolver.get()

        @singleton
        class SingletonClass(object):
            pass

        first = resolver(SingletonClass)
        second = resolver(SingletonClass)

        assert first is second

        Resolver.reset()

        resolver = Resolver.get()

        first = resolver(SingletonClass)
        second = resolver(SingletonClass)

        assert first is second

    def test_resetting_does_not_keep_undecorated_singletons(self):
        resolver = Resolver.get()

        class SingletonClass(object):
            pass

        resolver.singleton(SingletonClass)

        first = resolver(SingletonClass)
        second = resolver(SingletonClass)

        assert first is second

        Resolver.reset()

        resolver = Resolver.get()

        first = resolver(SingletonClass)
        second = resolver(SingletonClass)

        assert first is not second
