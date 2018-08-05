from typing import List
from unittest.mock import MagicMock

from bumblebee.host.api.manager import ApiManager
from bumblebee.host.framework.api.handler import Handler
from bumblebee.host.framework.recurring_task import RecurringTask


class FakeHandler(Handler):
    def __init__(self):
        self.task_a = MagicMock(RecurringTask)
        self.task_b = MagicMock(RecurringTask)
        self._tasks = [self.task_a, self.task_b]

    def tasks(self) -> List[RecurringTask]:
        return self._tasks


class TestApiManager(object):
    def test_adding_a_handler_adds_all_of_the_tasks(self, resolver):
        handler: FakeHandler = resolver(FakeHandler)
        manager: ApiManager = resolver(ApiManager)

        assert len(manager.handlers) == 0
        assert len(manager.tasks) == 0

        manager.add_handler(handler)

        assert len(manager.handlers) == 1
        assert len(manager.tasks) == len(handler.tasks())

    def test_starting_the_api_manager_starts_all_of_the_tasks(self, resolver):
        handler: FakeHandler = resolver(FakeHandler)
        manager: ApiManager = resolver(ApiManager)

        manager.add_handler(handler)

        manager.start()

        handler.task_a.start.assert_called_once()
        handler.task_b.start.assert_called_once()

    def test_starting_the_api_manager_starts_newly_added_handlers(self, resolver):
        handler: FakeHandler = resolver(FakeHandler)
        manager: ApiManager = resolver(ApiManager)

        manager.start()

        manager.add_handler(handler)

        handler.task_a.start.assert_called_once()
        handler.task_b.start.assert_called_once()

    def test_only_the_newly_added_tasks_are_started(self, resolver):
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
