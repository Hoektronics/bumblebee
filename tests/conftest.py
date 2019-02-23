from unittest.mock import Mock, MagicMock, call

import pytest

from bumblebee.host.framework.events import Event, EventManager
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


@pytest.fixture
def fakes_events(resolver):
    class EventAssertion(object):
        def __init__(self):
            self.events = []

        def __call__(self, event):
            self.events.append(event)

        def __bool__(self):
            return len(self.events) > 0

        def once(self):
            return self.times(1)

        def times(self, count):
            return len(self.events) == count

    class FakesEvents(object):
        def __init__(self):
            self._original: EventManager = resolver(EventManager)

            self._fire_function = lambda event: EventManager.fire(self._original, event)
            self._original.fire = MagicMock(side_effect=self._fire_function)

            self._event_assertions = {}

        def fake(self, event_class: type):
            if event_class not in self._event_assertions:
                self._event_assertions[event_class] = EventAssertion()

            def _internal(fired_event: Event):
                if isinstance(fired_event, event_class):
                    self._event_assertions[event_class](fired_event)
                else:
                    _internal.current_fire_function(fired_event)

            _internal.current_fire_function = self._fire_function

            self._fire_function = _internal
            self._original.fire.side_effect = self._fire_function

        def fired(self, event: Event) -> EventAssertion:
            return self._event_assertions[event]

    return FakesEvents()
