import pytest

from bumblebee.host.framework.ioc import Resolver


@pytest.fixture
def resolver():
    Resolver.reset()

    return Resolver.get()


@pytest.fixture
def dictionary_magic():
    def _dictionary_magic(mock):
        base = {}

        if hasattr(mock.__class__, '__getitem__'):
            mock.__getitem__.side_effect = base.__getitem__

        if hasattr(mock.__class__, '__contains__'):
            mock.__contains__.side_effect = base.__contains__

        if hasattr(mock.__class__, '__setitem__'):
            mock.__setitem__.side_effect = base.__setitem__

        if hasattr(mock.__class__, '__delitem__'):
            mock.__delitem__.side_effect = base.__delitem__

        return mock

    return _dictionary_magic
