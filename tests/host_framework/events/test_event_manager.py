from bumblebee.host_framework.events.event import EventBag, Event, EventManager


class FakeEvents(EventBag):
    class EventWithoutData(Event):
        pass


def test_firing_an_event_with_no_data_calls_bound_method_without_arguments():
    event = FakeEvents.EventWithoutData()
    method_called = False

    def bound_method():
        nonlocal method_called
        method_called = True

    event_manager = EventManager()
    event_manager.on(FakeEvents.EventWithoutData, bound_method)

    assert not method_called

    event_manager.fire(event)

    assert method_called

def test_firing_an_event_with_no_data_calls_bound_method_with_event_argument():
    method_called = False
    event = FakeEvents.EventWithoutData()

    def bound_method(fired_event):
        nonlocal method_called
        method_called = True
        assert event is fired_event

    event_manager = EventManager()
    event_manager.on(FakeEvents.EventWithoutData, bound_method)

    assert not method_called

    event_manager.fire(event)

    assert method_called
