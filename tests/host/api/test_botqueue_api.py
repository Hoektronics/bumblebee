from unittest.mock import Mock, MagicMock, PropertyMock

import pytest
from requests import Response

from bumblebee.host.api.botqueue_api import BotQueueApi, ErrorResponse
from bumblebee.host.api.rest import RestApi
from bumblebee.host.api.socket import WebSocketApi


class TestBotQueueApi(object):
    def test_command_calls_rest_api_if_socket_is_disconnected(self, resolver):
        socket_api = Mock(WebSocketApi)
        connected_mock = PropertyMock(return_value=False)
        type(socket_api).connected = connected_mock
        resolver.instance(socket_api)

        response = MagicMock(Response)
        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "status": "success",
            "data": {
                "foo": "bar",
            }
        }

        rest_api = Mock(RestApi)
        rest_api.post.return_value = response
        resolver.instance(rest_api)

        api = resolver(BotQueueApi)
        result = api.command("FakeTestCommand", {"some": "data"})

        connected_mock.assert_called()
        ok_mock.assert_called()

        rest_api.post.assert_called_with("/host", {
            "command": "FakeTestCommand",
            "data": {
                "some": "data",
            }
        })

        assert len(result) == 1
        assert "foo" in result
        assert result["foo"] == "bar"

    def test_data_parameter_is_not_needed(self, resolver):
        socket_api = Mock(WebSocketApi)
        connected_mock = PropertyMock(return_value=False)
        type(socket_api).connected = connected_mock
        resolver.instance(socket_api)

        response = MagicMock(Response)
        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "status": "success",
            "data": {
                "foo": "bar",
            }
        }

        rest_api = Mock(RestApi)
        rest_api.post.return_value = response
        resolver.instance(rest_api)

        api = resolver(BotQueueApi)
        result = api.command("FakeTestCommand")

        connected_mock.assert_called()
        ok_mock.assert_called()

        rest_api.post.assert_called_with("/host", {
            "command": "FakeTestCommand",
        })

        assert len(result) == 1
        assert "foo" in result
        assert result["foo"] == "bar"

    def test_command_calls_rest_api_and_raises_an_error(self, resolver):
        socket_api = Mock(WebSocketApi)
        connected_mock = PropertyMock(return_value=False)
        type(socket_api).connected = connected_mock
        resolver.instance(socket_api)

        response = MagicMock(Response)
        ok_mock = PropertyMock(return_value=False)
        type(response).ok = ok_mock
        response.json.return_value = {
            "status": "error",
            "code": 5,
            "message": "This is an error"
        }

        rest_api = Mock(RestApi)
        rest_api.post.return_value = response
        resolver.instance(rest_api)

        api = resolver(BotQueueApi)

        with pytest.raises(ErrorResponse) as exec_info:
            api.command("FakeTestCommand", {"some": "data"})

        connected_mock.assert_called()
        ok_mock.assert_called()
        assert exec_info.type is ErrorResponse
        assert exec_info.value.code == 5
        assert exec_info.value.message == "This is an error"
