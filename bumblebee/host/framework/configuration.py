from __future__ import annotations

import json
import os
from threading import Lock

from appdirs import AppDirs

from bumblebee.host.framework.ioc import Resolver


class AutoSavingDictionary(dict):
    def __init__(self, base: AutoSavingDictionary, _dictionary):
        self._base = base
        super().__init__()

        for key, value in _dictionary.items():
            self.__setitem__(key, value)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, AutoSavingDictionary):
            dict.__setitem__(self, key, AutoSavingDictionary(self, value))
        else:
            dict.__setitem__(self, key, value)
        self._save()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._save()

    def _save(self):
        self._base._save()


class Configuration(AutoSavingDictionary, object):
    def __init__(self, config_type):
        resolver = Resolver.get()
        app_dirs = resolver(AppDirs)

        config_file_name = '{type}.json'.format(type=config_type)
        self._config_directory = app_dirs.user_config_dir
        self._config_path = os.path.join(self._config_directory, config_file_name)

        super().__init__(self, self.__load_config())

        self._lock = Lock()
        self._save()

    def __load_config(self):
        if os.path.exists(self._config_path):
            with open(self._config_path, 'rb') as config_handle:
                return json.load(config_handle)

        return self._default_config()

    @staticmethod
    def _default_config():
        return {}

    def _save(self):
        os.makedirs(self._config_directory, exist_ok=True)

        with open(self._config_path, 'w') as config_handle:
            json.dump(self, config_handle)