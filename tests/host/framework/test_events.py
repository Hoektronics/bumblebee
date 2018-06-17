from bumblebee.host.framework.events import EventBag, Event, EventManager, on, bind_events


class FakeEvents(EventBag):
    class EventWithoutData(Event):
        pass


class TestEvents(object):
    def test_firing_an_event_with_no_data_calls_bound_method_without_arguments(self):
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

    def test_firing_an_event_with_no_data_calls_bound_method_with_event_argument(self):
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

    def test_binding_method_with_instance(self):
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

    def test_binding_method_with_class_method(self):
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

    def test_using_on_events(self, resolver):
        class FakeClassWithEvents(object):
            class_method_called = False

            def __init__(self):
                self.instance_method_called = False

            @on(FakeEvents.EventWithoutData)
            def instance_method(self):
                self.instance_method_called = True

            @classmethod
            @on(FakeEvents.EventWithoutData)
            def class_method(cls):
                cls.class_method_called = True

        test_object = FakeClassWithEvents()

        event_manager = resolver(EventManager)
        event_manager.bind(test_object)

        assert not test_object.instance_method_called
        assert not test_object.class_method_called

        event_manager.fire(FakeEvents.EventWithoutData())

        assert test_object.instance_method_called
        assert test_object.class_method_called

    def test_using_fire_on_event(self, resolver):
        event = FakeEvents.EventWithoutData()
        method_called = False

        def bound_method():
            nonlocal method_called
            method_called = True

        event_manager = resolver(EventManager)
        event_manager.on(FakeEvents.EventWithoutData, bound_method)

        assert not method_called

        event.fire()

        assert method_called

    def test_using_auto_binding_for_event_listener_classes(self):
        @bind_events
        class FakeClassWithEvents(object):
            def __init__(self):
                self.method_called = False

            @on(FakeEvents.EventWithoutData)
            def instance_method(self):
                self.method_called = True

        test_object = FakeClassWithEvents()

        assert not test_object.method_called

        FakeEvents.EventWithoutData().fire()

        assert test_object.method_called

    def test_using_auto_binding_with_resolved_class(self, resolver):
        class AnnotatedClass(object):
            pass

        @bind_events
        class FakeClassWithEvents(object):
            def __init__(self, foo: AnnotatedClass):
                self.method_called = False
                self.foo = foo

            @on(FakeEvents.EventWithoutData)
            def instance_method(self):
                self.method_called = True

        test_object = resolver(FakeClassWithEvents)

        assert isinstance(test_object.foo, AnnotatedClass)

        assert not test_object.method_called

        FakeEvents.EventWithoutData().fire()

        assert test_object.method_called
