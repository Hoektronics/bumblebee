from unittest.mock import MagicMock, patch, Mock, PropertyMock

from requests import Response

from bumblebee.host.api.rest import RestApi
from bumblebee.host.configurations import HostConfiguration


class TestRestApi(object):
    default_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def test_default_headers_are_set(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)
        config["server"] = "https://server/"

        api: RestApi = resolver(RestApi)

        assert "Content-Type" in api._headers
        assert api._headers["Content-Type"] == "application/json"
        assert "Accept" in api._headers
        assert api._headers["Accept"] == "application/json"
        assert "Authorization" not in api._headers

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {}

        with patch('bumblebee.host.api.rest.requests') as RequestsMock:
            post: Mock = RequestsMock.post
            post.return_value = response

            actual = api.post("/foo/bar")

            post.assert_called_with("https://server/foo/bar", json={}, headers=self.default_headers)

            assert actual is response

    def test_post_sends_headers(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)
        config["server"] = "https://server/"

        api: RestApi = resolver(RestApi)

        api._headers["Authorization"] = "Bearer token"

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {}

        with patch('bumblebee.host.api.rest.requests') as RequestsMock:
            post: Mock = RequestsMock.post
            post.return_value = response

            actual = api.post("/foo/bar")

            post.assert_called_with("https://server/foo/bar",
                                    json={},
                                    headers={"Authorization": "Bearer token", **self.default_headers}
                                    )

            assert actual is response

    def test_post_sends_data(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)
        config["server"] = "https://server/"

        api: RestApi = resolver(RestApi)

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {}

        with patch('bumblebee.host.api.rest.requests') as RequestsMock:
            post: Mock = RequestsMock.post
            post.return_value = response

            actual = api.post("/foo/bar", {"key": "value"})

            post.assert_called_with("https://server/foo/bar",
                                    json={"key": "value"},
                                    headers=self.default_headers
                                    )

            assert actual is response
