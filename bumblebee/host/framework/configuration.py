import json
import os
from threading import Lock

from appdirs import AppDirs

from bumblebee.host.framework.ioc import Resolver


class Configuration(object):
    def __init__(self, config_type):
        resolver = Resolver.get()
        app_dirs = resolver(AppDirs)

        config_file_name = '{type}.json'.format(type=config_type)
        self._config_directory = app_dirs.user_config_dir
        self._config_path = os.path.join(self._config_directory, config_file_name)

        self._config = self.__load_config()
        self._lock = Lock()
        self._save()

    def __load_config(self):
        if os.path.exists(self._config_path):
            with open(self._config_path, 'rb') as config_handle:
                return json.load(config_handle)

        return self._default_config()

    def __getitem__(self, item):
        with self._lock:
            return self._config[item]

    def __setitem__(self, key, value):
        with self._lock:
            self._config[key] = value
            self._save()

    def __contains__(self, key):
        return key in self._config

    def __delitem__(self, key):
        with self._lock:
            del self._config[key]
            self._save()

    @staticmethod
    def _default_config():
        return {}

    def _save(self):
        os.makedirs(self._config_directory, exist_ok=True)

        with open(self._config_path, 'w') as config_handle:
            json.dump(self._config, config_handle)