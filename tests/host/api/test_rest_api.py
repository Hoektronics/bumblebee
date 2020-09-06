from unittest.mock import MagicMock

from bumblebee.host.api.rest import RestApi
from bumblebee.host.api.server import Server
from bumblebee.host.configurations import HostConfiguration


class TestRestApi(object):
    default_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def test_default_headers_are_set(self, resolver, mock_session, fake_responses):
        resolver.instance(resolver(Server, url="https://server/"))

        api: RestApi = resolver(RestApi)

        assert "Content-Type" in api.session.headers
        assert api.session.headers["Content-Type"] == "application/json"
        assert "Accept" in api.session.headers
        assert api.session.headers["Accept"] == "application/json"
        assert "Authorization" not in api.session.headers

        response = fake_responses.ok()
        api.session.post.return_value = response

        actual = api.post("/foo/bar")

        api.session.post.assert_called_with("https://server/foo/bar", json={})

        assert actual is response

    def test_post_sends_headers(self, resolver, mock_session, fake_responses):
        server = resolver(Server, url="https://server/")
        resolver.instance(server)

        api: RestApi = resolver(RestApi)

        server.access_token = "token"
        assert "Authorization" not in api.session.headers

        response = fake_responses.ok()
        api.session.post.return_value = response

        actual = api.post("/foo/bar")

        api.session.post.assert_called_with("https://server/foo/bar", json={})

        assert actual is response

        assert "Authorization" in api.session.headers
        assert api.session.headers["Authorization"] == "Bearer token"

    def test_post_sends_data(self, resolver, mock_session, fake_responses):
        server = resolver(Server, url="https://server/")
        resolver.instance(server)

        api: RestApi = resolver(RestApi)

        response = fake_responses.ok()
        api.session.post.return_value = response

        actual = api.post("/foo/bar", {"key": "value"})

        api.session.post.assert_called_with("https://server/foo/bar", json={"key": "value"})

        assert actual is response
