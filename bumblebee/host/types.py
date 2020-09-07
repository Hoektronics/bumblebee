import json


class User(object):
    def __init__(self,
                 id: int,
                 username: str):
        self.id = id
        self.username = username


class HostRequest(object):
    def __init__(self,
                 id: int,
                 status: str,
                 server: str):
        self.id = id
        self.status = status
        self.server = server

    @property
    def url(self):
        return f"{self.server}/hosts/requests/{self.id}"


class Host(object):
    def __init__(self,
                 id: int,
                 name: str):
        self.id = id
        self.name = name


class Job(object):
    def __init__(self,
                 id: int,
                 name: str,
                 status: str,
                 file_url: str):
        self.id = id
        self.name = name
        self.status = status
        self.file_url = file_url


class Bot(object):
    def __init__(self,
                 id: int,
                 name: str,
                 status: str,
                 type: str,
                 current_job: Job = None,
                 driver=None):
        self.id = id
        self.name = name
        self.status = status
        self.type = type
        self.current_job = current_job

        if driver is not None \
                and not isinstance(driver, dict) \
                and isinstance(driver, str):
            driver = json.loads(driver)
        self.driver = driver
