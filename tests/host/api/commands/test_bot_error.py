from unittest.mock import Mock

from bumblebee.host.api.botqueue_api import BotQueueApi
from bumblebee.host.api.commands.bot_error import BotError


class TestBotError(object):
    def test_sending_error_string(self, resolver):
        api = Mock(BotQueueApi)
        api.command.return_value = {}
        resolver.instance(api)

        bot_error = resolver(BotError)

        bot_error(1, "Failure")

        api.command.assert_called_with("BotError", {
            "id": 1,
            "error": "Failure"
        })

    def test_sending_real_exception(self, resolver):
        api = Mock(BotQueueApi)
        api.command.return_value = {}
        resolver.instance(api)

        bot_error = resolver(BotError)

        try:
            raise Exception("Failure")
        except Exception as ex:
            bot_error(1, ex)

        api.command.assert_called_once()
        call_args = api.command.call_args[0]
        assert call_args[0] == 'BotError'
        assert call_args[1]['id'] == 1
        assert call_args[1]['error'].startswith('Traceback')
