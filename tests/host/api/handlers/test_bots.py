from unittest.mock import MagicMock, Mock, PropertyMock

from requests import Response

from bumblebee.host.api.handlers.bots import BotsHandler
from bumblebee.host.api.rest import RestApi
from bumblebee.host.events import BotEvents, JobEvents
from bumblebee.host.framework.recurring_task import RecurringTask


class TestBotsHandler(object):
    def test_tasks_returns_polling_task(self, resolver):
        rest = Mock(RestApi)
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        tasks = handler.tasks()

        assert len(tasks) == 1
        poll_task: RecurringTask = tasks[0]
        assert poll_task.interval == 60
        assert poll_task.function == handler.poll

    def test_polling_calls_the_right_endpoint(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        rest = Mock(RestApi)
        rest.with_token.return_value = rest
        response = MagicMock(Response)
        rest.get.return_value = response

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "data": []
        }
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        handler.poll()

        rest.with_token.assert_called_once()
        rest.get.assert_called_once_with("/host/bots")

        assert not fakes_events.fired(BotEvents.BotAdded)
        assert not fakes_events.fired(BotEvents.BotRemoved)

    def test_polling_adds_a_bot_it_has_not_seen_before(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        rest = Mock(RestApi)
        rest.with_token.return_value = rest
        response = MagicMock(Response)
        rest.get.return_value = response

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "data": [
                {
                    "id": 1,
                    "name": "Test bot",
                    "type": "3d_printer",
                    "status": "Offline"
                }
            ]
        }
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        handler.poll()

        rest.with_token.assert_called_once()
        rest.get.assert_called_once_with("/host/bots")

        assert fakes_events.fired(BotEvents.BotAdded)
        assert not fakes_events.fired(BotEvents.BotRemoved)

    def test_polling_adds_a_bot_only_once(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        rest = Mock(RestApi)
        rest.with_token.return_value = rest

        response = MagicMock(Response)
        rest.get.return_value = response

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "Offline"}
        response.json.side_effect = [
            {
                "data": [
                    bot
                ]
            },
            {
                "data": [
                    bot
                ]
            }
        ]
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        handler.poll()
        handler.poll()

        rest.with_token.assert_called()
        rest.get.assert_called_with("/host/bots")

        fired = fakes_events.fired(BotEvents.BotAdded)
        assert fired.once()
        assert not fakes_events.fired(BotEvents.BotRemoved)

    def test_polling_removes_the_bot(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        rest = Mock(RestApi)
        rest.with_token.return_value = rest
        response = MagicMock(Response)
        rest.get.return_value = response

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "Offline"}
        response.json.side_effect = [
            {
                "data": [
                    bot
                ]
            },
            {
                "data": []
            }
        ]
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        handler.poll()
        handler.poll()

        rest.with_token.assert_called()
        rest.get.assert_called_with("/host/bots")

        added = fakes_events.fired(BotEvents.BotAdded)
        assert added.once()
        removed = fakes_events.fired(BotEvents.BotRemoved)
        assert removed.once()

    def test_polling_will_add_the_bot_back(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        rest = Mock(RestApi)
        rest.with_token.return_value = rest
        response = MagicMock(Response)
        rest.get.return_value = response

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "Offline"}
        response.json.side_effect = [
            {
                "data": [
                    bot
                ]
            },
            {
                "data": []
            },
            {
                "data": [
                    bot
                ]
            }
        ]
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        handler.poll()
        handler.poll()
        handler.poll()

        rest.with_token.assert_called()
        rest.get.assert_called_with("/host/bots")

        added = fakes_events.fired(BotEvents.BotAdded)
        assert added.times(2)
        removed = fakes_events.fired(BotEvents.BotRemoved)
        assert removed.once()

    def test_polling_will_fire_bot_updated_on_update(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotUpdated)

        rest = Mock(RestApi)
        rest.with_token.return_value = rest
        response = MagicMock(Response)
        rest.get.return_value = response

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock

        response.json.side_effect = [
            {
                "data": [
                    {
                        "id": 1,
                        "name": "Test bot",
                        "type": "3d_printer",
                        "status": "Offline"
                    }
                ]
            },
            {
                "data": [
                    {
                        "id": 1,
                        "name": "Test bot",
                        "type": "3d_printer",
                        "status": "Idle"
                    }
                ]
            }
        ]
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        handler.poll()
        handler.poll()

        rest.with_token.assert_called()
        rest.get.assert_called_with("/host/bots")

        assert fakes_events.fired(BotEvents.BotAdded).once()
        assert fakes_events.fired(BotEvents.BotUpdated).once()

    def test_polling_will_emit_assigned_job(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(JobEvents.JobAssigned)

        rest = Mock(RestApi)
        rest.with_token.return_value = rest
        response = MagicMock(Response)
        rest.get.return_value = response

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock

        response.json.side_effect = [
            {
                "data": [
                    {
                        "id": 1,
                        "name": "Test bot",
                        "type": "3d_printer",
                        "status": "Offline",
                        "job": {
                            "id": 1,
                            "status": "assigned"
                        }
                    }
                ]
            }
        ]
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        handler.poll()

        rest.with_token.assert_called()
        rest.get.assert_called_with("/host/bots")

        assert fakes_events.fired(BotEvents.BotAdded).once()
        assert fakes_events.fired(JobEvents.JobAssigned).once()

    def test_polling_will_emit_assigned_job_only_once(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(JobEvents.JobAssigned)

        rest = Mock(RestApi)
        rest.with_token.return_value = rest
        response = MagicMock(Response)
        rest.get.return_value = response

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock

        job = {"id": 1, "status": "assigned"}
        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "Offline", "job": job}
        response_object = {"data": [bot]}
        response.json.side_effect = [
            response_object,
            response_object
        ]
        resolver.instance(rest)

        handler = resolver(BotsHandler)
        handler.poll()

        rest.with_token.assert_called()
        rest.get.assert_called_with("/host/bots")

        assert fakes_events.fired(BotEvents.BotAdded).once()
        assert fakes_events.fired(JobEvents.JobAssigned).once()
