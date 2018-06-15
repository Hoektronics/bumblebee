import pytest

from bumblebee.host.framework.ioc import Resolver, FailureToBindException


class NoArgumentFakeClass(object):
    pass


class OneArgumentFakeClass(object):
    def __init__(self, foo: NoArgumentFakeClass):
        self.foo = foo


class UnannotatedFakeClass(object):
    def __init__(self, foo):
        self.foo = foo


def test_can_resolve_given_instance():
    resolver = Resolver()

    instance = NoArgumentFakeClass()

    resolver.instance(NoArgumentFakeClass, instance)

    fake_class = resolver(NoArgumentFakeClass)

    assert isinstance(fake_class, NoArgumentFakeClass)
    assert fake_class is instance


def test_can_resolve_given_only_instance():
    resolver = Resolver()

    instance = NoArgumentFakeClass()

    resolver.instance(instance)

    fake_class = resolver(NoArgumentFakeClass)

    assert isinstance(fake_class, NoArgumentFakeClass)
    assert fake_class is instance


def test_can_resolve_explicitly_bound_class():
    resolver = Resolver()

    resolver.bind(NoArgumentFakeClass)

    fake_class = resolver(NoArgumentFakeClass)

    assert isinstance(fake_class, NoArgumentFakeClass)


def test_can_resolve_singleton_function():
    resolver = Resolver()

    def resolve_instance():
        return NoArgumentFakeClass()

    resolver.singleton(NoArgumentFakeClass, resolve_instance)

    fake_class_first_time = resolver(NoArgumentFakeClass)

    assert isinstance(fake_class_first_time, NoArgumentFakeClass)

    fake_class_second_time = resolver(NoArgumentFakeClass)

    assert isinstance(fake_class_second_time, NoArgumentFakeClass)
    assert fake_class_second_time is fake_class_first_time


def test_can_resolve_implicitly_bound_class():
    resolver = Resolver()

    fake_class = resolver(NoArgumentFakeClass)

    assert isinstance(fake_class, NoArgumentFakeClass)


def test_can_resolve_chain_of_classes_based_on_type_hinting():
    resolver = Resolver()

    fake_class: OneArgumentFakeClass = resolver(OneArgumentFakeClass)

    assert isinstance(fake_class, OneArgumentFakeClass)
    assert isinstance(fake_class.foo, NoArgumentFakeClass)


def test_can_resolve_chain_using_instance():
    resolver = Resolver()

    instance = NoArgumentFakeClass()

    resolver.instance(NoArgumentFakeClass, instance)

    fake_class: OneArgumentFakeClass = resolver(OneArgumentFakeClass)

    assert isinstance(fake_class, OneArgumentFakeClass)
    assert isinstance(fake_class.foo, NoArgumentFakeClass)
    assert fake_class.foo is instance


def test_cannot_resolve_unannotated_parameters():
    resolver = Resolver()

    with pytest.raises(FailureToBindException):
        resolver(UnannotatedFakeClass)