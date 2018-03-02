from requests import Session
from urlparse import urljoin


class BotQueueAPI(object):
    def __init__(self, config):
        self._config = config
        self._session = Session()
        self._session.verify = False
        self.__access_token = None
        self.update_auth()

    def update_auth(self):
        if "host" in self._config and "access_token" in self._config["host"]:
            self.__access_token = self._config["host"]["access_token"]
            self._session.headers.update({'Authorization': 'Bearer %s' % self.__access_token})
        else:
            self.__access_token = None

    def __post(self, url, payload=None):
        if payload is not None:
            payload = []

        url = urljoin(self._config['server'], url)

        print('Posting %s to %s' % (payload, url))

        return self._session.post(url, payload)

    def __get(self, url):
        url = urljoin(self._config['server'], url)

        print('Getting %s' % url)

        return self._session.get(url)

    def host_request(self):
        if "host_request_id" in self._config:
            return self.request_status(self._config["host_request_id"])

        response = self.__post('/host/requests')

        json_response = response.json()

        host_request_id = json_response['data']['id']
        self._config["host_request_id"] = host_request_id
        self._config.save()

        return json_response['data']

    def request_status(self, host_request_id):
        response = self.__get('/host/requests/{host_request_id}'.format(host_request_id=host_request_id))

        return response.json()['data']

    def get_host(self, host_request_id):
        response = self.__post('/host/requests/{host_request_id}/access'.format(host_request_id=host_request_id))

        print(response.content)
        return response.json()['data']

    def is_access_valid(self):
        if "host" not in self._config or "access_token" not in self._config["host"]:
            return False

        response = self.__post('/host/refresh')

        if "host" not in self._config:
            self._config['host'] = []
        self._config['host']['access_token'] = response.json()['access_token']
        self._config.save()
        self.update_auth()
        return True

    def get_bots(self):
        response = self.__get('/host/bots')

        return response.json()['data']