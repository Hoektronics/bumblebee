import pytest

from bumblebee.host.framework.ioc import Resolver


@pytest.fixture
def resolver():
    Resolver.reset()

    return Resolver.get()
