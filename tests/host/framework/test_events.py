from bumblebee.host.framework.events import EventBag, Event, EventManager, on


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


def test_binding_method_with_instance():
    class TestObject(object):
        def __init__(self):
            self.callback_called = False

        def unbound_method(self):
            self.callback_called = True

    test_object = TestObject()

    event_manager = EventManager()
    event_manager.add_unbound_method(FakeEvents.EventWithoutData, TestObject.unbound_method)

    event_manager.bind(test_object)

    assert not test_object.callback_called

    event_manager.fire(FakeEvents.EventWithoutData())

    assert test_object.callback_called


def test_binding_method_with_class_method():
    class TestObject(object):
        callback_called = False

        @classmethod
        def unbound_class_method(cls):
            cls.callback_called = True

    test_object = TestObject()

    event_manager = EventManager()
    event_manager.add_unbound_method(FakeEvents.EventWithoutData, TestObject.unbound_class_method)

    event_manager.bind(test_object)

    assert not test_object.callback_called

    event_manager.fire(FakeEvents.EventWithoutData())

    assert test_object.callback_called
    assert TestObject.callback_called


# def test_using_on_events():
#     class FakeClassWithEvents(object):
#         class_method_called = False
#         def __init__(self):
#             self.instance_method_called = False
#
#         @on(FakeEvents.EventWithoutData)
#         def instance_method(self):
#             self.instance_method_called = True
#
#         @classmethod
#         @on(FakeEvents.EventWithoutData)
#         def class_method(cls):
#             cls.class_method_called = True
#
#     test_object = FakeClassWithEvents()
#
#     event_manager = EventManager()
#     event_manager.bind(test_object)
#
#     assert not test_object.instance_method_called
#     assert not test_object.class_method_called
#
#     event_manager.fire(FakeEvents.EventWithoutData())
#
#     assert test_object.instance_method_called
#     assert test_object.class_method_called
