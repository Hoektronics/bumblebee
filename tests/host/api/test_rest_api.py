from unittest.mock import MagicMock, patch, Mock, PropertyMock

import pytest
from requests import Response

from bumblebee.host.api.rest import RestApi, AccessTokenNotFound
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

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {}

        with patch('bumblebee.host.api.rest.requests') as RequestsMock:
            get: Mock = RequestsMock.get
            get.return_value = response

            actual = api.get("/foo/bar")

            get.assert_called_with("https://server/foo/bar", headers=self.default_headers)

            assert actual is response

    def test_with_token_throws_access_token_not_found_if_access_token_is_not_available(self, resolver):
        config = MagicMock(HostConfiguration)
        resolver.instance(config)

        api: RestApi = resolver(RestApi)

        with pytest.raises(AccessTokenNotFound):
            api.with_token()

    def test_with_token_updates_session(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)

        config["access_token"] = "token"

        api: RestApi = resolver(RestApi)

        new_api = api.with_token()

        assert new_api is not api

        assert "Authorization" not in api._headers

        assert "Authorization" in new_api._headers
        assert new_api._headers["Authorization"] == "Bearer token"

    def test_get_sends_headers(self, resolver, dictionary_magic):
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
            get: Mock = RequestsMock.get
            get.return_value = response

            actual = api.get("/foo/bar")

            get.assert_called_with("https://server/foo/bar",
                                   headers={"Authorization": "Bearer token", **self.default_headers}
                                   )

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

    def test_put_sends_headers(self, resolver, dictionary_magic):
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
            put: Mock = RequestsMock.put
            put.return_value = response

            actual = api.put("/foo/bar")

            put.assert_called_with("https://server/foo/bar",
                                    json={},
                                    headers={"Authorization": "Bearer token", **self.default_headers}
                                    )

            assert actual is response

    def test_put_sends_data(self, resolver, dictionary_magic):
        config = dictionary_magic(MagicMock(HostConfiguration))
        resolver.instance(config)
        config["server"] = "https://server/"

        api: RestApi = resolver(RestApi)

        response = MagicMock(Response)

        ok_mock = PropertyMock(return_value=True)
        type(response).ok = ok_mock
        response.json.return_value = {}

        with patch('bumblebee.host.api.rest.requests') as RequestsMock:
            put: Mock = RequestsMock.put
            put.return_value = response

            actual = api.put("/foo/bar", {"key": "value"})

            put.assert_called_with("https://server/foo/bar",
                                    json={"key": "value"},
                                    headers=self.default_headers
                                    )

            assert actual is response