from unittest.mock import Mock, MagicMock

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
    class FakesEvents(object):
        def __init__(self):
            self._original: EventManager = resolver(EventManager)

            self._fire_function = lambda event: EventManager.fire(self._original, event)
            self._original.fire = MagicMock(side_effect = self._fire_function)

            self._fired_events = {}

        def fake(self, *event_classes: type):
            for event_class in event_classes:
                def _internal(fired_event: Event):
                    if isinstance(fired_event, event_class):
                        if event_class not in self._fired_events:
                            self._fired_events[event_class] = []

                        self._fired_events[event_class].append(fired_event)
                    else:
                        self._fire_function(fired_event)

                self._fire_function = _internal

            self._original.fire.side_effect = self._fire_function

        def fired(self, event: Event):
            return event in self._fired_events

    return FakesEvents()
