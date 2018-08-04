from threading import Event
from unittest.mock import MagicMock

from bumblebee.host.framework.recurring_task import RecurringTask


class TestRecurringTask(object):
    def test_task_runs_on_start(self):
        interval = 1
        mock_function = MagicMock()
        task = RecurringTask(interval, mock_function)

        mock_event = MagicMock(Event)
        task.cancelled = mock_event

        mock_event.is_set.side_effect = [
            False,
            True
        ]

        task.start()

        mock_function.assert_called_once()
        mock_event.wait.assert_called_once_with(interval)

    def test_task_never_calls_function_if_cancelled(self):
        interval = 1
        mock_function = MagicMock()
        task = RecurringTask(interval, mock_function)

        mock_event = MagicMock(Event)
        task.cancelled = mock_event

        mock_event.is_set.return_value = True

        task.start()

        mock_function.assert_not_called()
        mock_event.wait.assert_not_called()

    def test_task_event_is_set_if_cancel_is_called(self):
        interval = 1
        mock_function = MagicMock()
        task = RecurringTask(interval, mock_function)

        mock_event = MagicMock(Event)
        task.cancelled = mock_event

        task.cancel()

        mock_event.set.assert_called_once()
