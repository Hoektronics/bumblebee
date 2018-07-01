from unittest.mock import MagicMock, PropertyMock

from requests import Response

from bumblebee.host.api.rest import RestApi
from bumblebee.host.api.queries.show_host_request import ShowHostRequest
from bumblebee.host.configurations import HostConfiguration


class TestShowHostRequest(object):
    def test_showing_host_request(self, resolver, dictionary_magic, fakes_events):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["host_request_id"] = "request_id"

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {
            "data": {
                "id": "request_id",
                "status": "request_status"
            }
        }

        api = MagicMock(RestApi)
        api.get.return_value = response
        resolver.instance(api)

        show_host_request = resolver(ShowHostRequest)

        request_data = show_host_request()

        api.get.assert_called_with("/host/requests/request_id")

        ok_mock.assert_called()
        response.json.assert_called()

        assert "id" in request_data
        assert request_data["id"] == "request_id"
        assert request_data["status"] == "request_status"

        assert "host_request_id" in config
