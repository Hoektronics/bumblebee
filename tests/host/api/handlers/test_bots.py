from unittest.mock import MagicMock, Mock, PropertyMock

from requests import Response

from bumblebee.host.api.botqueue_api import BotQueueApi
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

        api = Mock(BotQueueApi)
        api.command.return_value = []
        resolver.instance(api)

        handler = resolver(BotsHandler)
        handler.poll()

        api.command.assert_called_once_with("GetBots")

        assert not fakes_events.fired(BotEvents.BotAdded)
        assert not fakes_events.fired(BotEvents.BotRemoved)

    def test_polling_adds_a_bot_it_has_not_seen_before(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        api = Mock(BotQueueApi)
        api.command.return_value = [
            {
                "id": 1,
                "name": "Test bot",
                "type": "3d_printer",
                "status": "Offline",
                "driver": {
                    "type": "dummy"
                }
            }
        ]
        resolver.instance(api)
        resolver.instance(api)

        handler = resolver(BotsHandler)
        handler.poll()

        api.command.assert_called_once_with("GetBots")

        bot_added_event_assertion = fakes_events.fired(BotEvents.BotAdded)
        assert bot_added_event_assertion.once()
        assert not fakes_events.fired(BotEvents.BotRemoved)

        event: BotEvents.BotAdded = bot_added_event_assertion.event
        assert event.bot.id == 1
        assert event.bot.name == "Test bot"
        assert event.bot.status == "Offline"
        assert event.bot.type == "3d_printer"
        assert event.bot.driver == {"type": "dummy"}
        assert event.bot.current_job is None

    def test_polling_adds_a_bot_only_once(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "Offline", "driver": None}

        api = Mock(BotQueueApi)
        api.command.side_effect = [
            [bot],
            [bot]
        ]
        resolver.instance(api)

        handler = resolver(BotsHandler)
        handler.poll()
        handler.poll()

        api.command.assert_called_with("GetBots")

        bot_added_event_assertion = fakes_events.fired(BotEvents.BotAdded)
        assert bot_added_event_assertion.once()
        assert not fakes_events.fired(BotEvents.BotRemoved)

        event: BotEvents.BotAdded = bot_added_event_assertion.event
        assert event.bot.id == 1
        assert event.bot.name == "Test bot"
        assert event.bot.status == "Offline"
        assert event.bot.type == "3d_printer"
        assert event.bot.driver is None
        assert event.bot.current_job is None

    def test_polling_removes_the_bot(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "Offline", "driver": None}
        api = Mock(BotQueueApi)
        api.command.side_effect = [
            [bot],
            []
        ]
        resolver.instance(api)

        handler = resolver(BotsHandler)
        handler.poll()
        handler.poll()

        api.command.assert_called_with("GetBots")

        bot_added_event_assertion = fakes_events.fired(BotEvents.BotAdded)
        assert bot_added_event_assertion.once()
        bot_removed_event_assertion = fakes_events.fired(BotEvents.BotRemoved)
        assert bot_removed_event_assertion.once()

        bot_added_event = bot_added_event_assertion.event
        assert bot_added_event.bot.id == 1
        assert bot_added_event.bot.name == "Test bot"
        assert bot_added_event.bot.status == "Offline"
        assert bot_added_event.bot.type == "3d_printer"
        assert bot_added_event.bot.driver is None
        assert bot_added_event.bot.current_job is None

        bot_removed_event = bot_removed_event_assertion.event
        assert bot_removed_event.bot.id == 1
        assert bot_removed_event.bot.name == "Test bot"
        assert bot_removed_event.bot.status == "Offline"
        assert bot_removed_event.bot.type == "3d_printer"
        assert bot_removed_event.bot.driver is None
        assert bot_removed_event.bot.current_job is None

    def test_polling_will_add_the_bot_back(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotRemoved)

        bot = {"id": 1, "name": "Test bot", "type": "3d_printer", "status": "Offline", "driver": None}
        api = Mock(BotQueueApi)
        api.command.side_effect = [
            [bot],
            [],
            [bot]
        ]
        resolver.instance(api)

        handler = resolver(BotsHandler)
        handler.poll()
        handler.poll()
        handler.poll()

        api.command.assert_called_with("GetBots")

        bot_added_event_assertion = fakes_events.fired(BotEvents.BotAdded)
        assert bot_added_event_assertion.times(2)
        bot_removed_event_assertion = fakes_events.fired(BotEvents.BotRemoved)
        assert bot_removed_event_assertion.once()

        for event in bot_added_event_assertion.events:
            assert event.bot.id == 1
            assert event.bot.name == "Test bot"
            assert event.bot.status == "Offline"
            assert event.bot.type == "3d_printer"
            assert event.bot.driver is None
            assert event.bot.current_job is None

        bot_removed_event = bot_removed_event_assertion.event
        assert bot_removed_event.bot.id == 1
        assert bot_removed_event.bot.name == "Test bot"
        assert bot_removed_event.bot.status == "Offline"
        assert bot_removed_event.bot.type == "3d_printer"
        assert bot_removed_event.bot.driver is None
        assert bot_removed_event.bot.current_job is None

    def test_polling_will_fire_bot_updated_on_update(self, resolver, fakes_events):
        fakes_events.fake(BotEvents.BotAdded)
        fakes_events.fake(BotEvents.BotUpdated)

        api = Mock(BotQueueApi)
        api.command.side_effect = [
            [
                {
                    "id": 1,
                    "name": "Test bot",
                    "type": "3d_printer",
                    "status": "Offline",
                    "driver": None
                }
            ],
            [
                {
                    "id": 1,
                    "name": "Test bot",
                    "type": "3d_printer",
                    "status": "Idle",
                    "driver": None
                }
            ]
        ]
        resolver.instance(api)

        handler = resolver(BotsHandler)
        handler.poll()
        handler.poll()

        api.command.assert_called_with("GetBots")

        bot_added_event_assertion = fakes_events.fired(BotEvents.BotAdded)
        assert bot_added_event_assertion.once()
        bot_updated_event_assertion = fakes_events.fired(BotEvents.BotUpdated)
        assert bot_updated_event_assertion.once()

        bot_added_event = bot_added_event_assertion.event
        assert bot_added_event.bot.id == 1
        assert bot_added_event.bot.name == "Test bot"
        assert bot_added_event.bot.status == "Offline"
        assert bot_added_event.bot.type == "3d_printer"
        assert bot_added_event.bot.driver is None
        assert bot_added_event.bot.current_job is None

        bot_updated_event = bot_updated_event_assertion.event
        assert bot_updated_event.bot.id == 1
        assert bot_updated_event.bot.name == "Test bot"
        assert bot_updated_event.bot.status == "Idle"
        assert bot_updated_event.bot.type == "3d_printer"
        assert bot_updated_event.bot.driver is None
        assert bot_updated_event.bot.current_job is None
