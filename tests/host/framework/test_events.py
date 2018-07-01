from bumblebee.host.framework.events import EventBag, Event, EventManager, on, bind_events


class FakeEvents(EventBag):
    class EventWithoutData(Event):
        pass

    class EventOne(Event):
        pass

    class EventTwo(Event):
        pass

    class EventWithOneKwarg(Event):
        def __init__(self, name=None):
            self.name = name

    class EventWithTwoKwargs(Event):
        def __init__(self, name=None, stuff=None):
            self.name = name
            self.stuff = stuff

    class EventForCheckingAllProperties(Event):
        def __init__(self, name=None):
            self.name = name
            self.stuff = 5


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

    def test_wrapping_function_with_two_events_works(self):
        @bind_events
        class FakeClassWithEvents(object):
            def __init__(self):
                self.method_called_count = 0

            @on(FakeEvents.EventOne)
            @on(FakeEvents.EventTwo)
            def instance_method(self):
                self.method_called_count += 1

        test_object = FakeClassWithEvents()

        assert test_object.method_called_count == 0

        FakeEvents.EventOne().fire()

        assert test_object.method_called_count == 1

        FakeEvents.EventTwo().fire()

        assert test_object.method_called_count == 2

    def test_using_instance_of_an_event_in_decorator_works(self):
        @bind_events
        class FakeClassWithEvents(object):
            def __init__(self):
                self.method_called = False

            @on(FakeEvents.EventWithoutData())
            def instance_method(self):
                self.method_called = True

        test_object = FakeClassWithEvents()

        assert not test_object.method_called

        FakeEvents.EventWithoutData().fire()

        assert test_object.method_called

    def test_using_single_kwarg_to_filter_events_works(self):
        @bind_events
        class FakeClassWithEvents(object):
            def __init__(self):
                self.method_called = False

            @on(FakeEvents.EventWithOneKwarg(name="foo"))
            def instance_method(self):
                self.method_called = True

        test_object = FakeClassWithEvents()

        assert not test_object.method_called

        FakeEvents.EventWithOneKwarg(name="bar").fire()

        assert not test_object.method_called

        FakeEvents.EventWithOneKwarg(name="foo").fire()

        assert test_object.method_called

    def test_using_part_of_all_kwargs_to_filter_events_works(self):
        @bind_events
        class FakeClassWithEvents(object):
            def __init__(self):
                self.method_called = False

            @on(FakeEvents.EventWithTwoKwargs(name="foo"))
            def instance_method(self):
                self.method_called = True

        test_object = FakeClassWithEvents()

        assert not test_object.method_called

        FakeEvents.EventWithTwoKwargs(name="bar", stuff="other").fire()

        assert not test_object.method_called

        FakeEvents.EventWithTwoKwargs(name="foo", stuff="other").fire()

        assert test_object.method_called


    def test_manager_uses_properties_and_not_init_method_to_filter_events(self):
        @bind_events
        class FakeClassWithEvents(object):
            def __init__(self):
                self.method_called = False

            @on(FakeEvents.EventForCheckingAllProperties(name="foo"))
            def instance_method(self):
                self.method_called = True

        test_object = FakeClassWithEvents()

        assert not test_object.method_called

        first_event = FakeEvents.EventForCheckingAllProperties(name="foo")
        first_event.stuff += 1
        first_event.fire()

        assert not test_object.method_called

        FakeEvents.EventForCheckingAllProperties(name="foo").fire()

        assert test_object.method_called
