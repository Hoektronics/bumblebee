from typing import List
from unittest.mock import MagicMock, Mock

from bumblebee.host.api.manager import ApiManager
from bumblebee.host.api.socket import WebSocketApi
from bumblebee.host.configurations import HostConfiguration
from bumblebee.host.events import AuthFlowEvents
from bumblebee.host.framework.api.handler import Handler
from bumblebee.host.framework.recurring_task import RecurringTask
from bumblebee.host.types import Host


class FakeHandler(Handler):
    def __init__(self):
        self.task_a = MagicMock(RecurringTask)
        self.task_b = MagicMock(RecurringTask)
        self._tasks = [self.task_a, self.task_b]

    def tasks(self) -> List[RecurringTask]:
        return self._tasks


class TestApiManager(object):
    def test_adding_a_handler_adds_all_of_the_tasks(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        socket = Mock(WebSocketApi)
        resolver.instance(socket)

        handler: FakeHandler = resolver(FakeHandler)
        manager: ApiManager = resolver(ApiManager)

        assert len(manager.handlers) == 0
        assert len(manager.tasks) == 0

        manager.add_handler(handler)

        assert len(manager.handlers) == 1
        assert len(manager.tasks) == len(handler.tasks())

    def test_starting_the_api_manager_starts_all_of_the_tasks(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        socket = Mock(WebSocketApi)
        resolver.instance(socket)

        handler: FakeHandler = resolver(FakeHandler)
        manager: ApiManager = resolver(ApiManager)

        manager.add_handler(handler)

        manager.start()

        handler.task_a.start.assert_called_once()
        handler.task_b.start.assert_called_once()

    def test_starting_the_api_manager_starts_newly_added_handlers(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        socket = Mock(WebSocketApi)
        resolver.instance(socket)

        handler: FakeHandler = resolver(FakeHandler)
        manager: ApiManager = resolver(ApiManager)

        manager.start()

        manager.add_handler(handler)

        handler.task_a.start.assert_called_once()
        handler.task_b.start.assert_called_once()

    def test_only_the_newly_added_tasks_are_started(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        socket = Mock(WebSocketApi)
        resolver.instance(socket)

        handler_a: FakeHandler = resolver(FakeHandler)
        handler_b: FakeHandler = resolver(FakeHandler)
        manager: ApiManager = resolver(ApiManager)

        manager.add_handler(handler_a)

        manager.start()

        manager.add_handler(handler_b)

        handler_a.task_a.start.assert_called_once()
        handler_a.task_b.start.assert_called_once()
        handler_b.task_a.start.assert_called_once()
        handler_b.task_b.start.assert_called_once()

    def test_handler_subscribes_to_host_channel_on_creation_if_possible(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["id"] = 1

        socket = Mock(WebSocketApi)
        resolver.instance(socket)

        resolver(ApiManager)

        socket.subscribe.assert_called_with('private-host.1')

    def test_handler_subscribes_to_host_channel_later_if_host_is_made(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        socket = Mock(WebSocketApi)
        resolver.instance(socket)

        resolver(ApiManager)

        socket.subscribe.assert_not_called()

        host = Host(
            id=1,
            name="Test Host"
        )

        AuthFlowEvents.HostMade(host).fire()

        socket.subscribe.assert_called_with('private-host.1')

