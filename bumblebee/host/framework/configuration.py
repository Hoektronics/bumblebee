import json
import os
from threading import Lock

from appdirs import AppDirs

from bumblebee.host.framework.ioc import Resolver


class AutoSavingDictionary(object):
    def __init__(self, base: 'AutoSavingDictionary', _dictionary):
        self._base = base
        self._dictionary = _dictionary

    def __getitem__(self, item):
        if isinstance(self._dictionary[item], dict):
            return AutoSavingDictionary(self, self._dictionary[item])
        else:
            return self._dictionary[item]

    def __setitem__(self, key, value):
        if isinstance(value, AutoSavingDictionary):
            self._dictionary[key] = value._dictionary
        else:
            self._dictionary[key] = value
        self._base._save()

    def __contains__(self, item):
        return item in self._dictionary

    def __delitem__(self, key):
        del self._dictionary[key]
        self._base._save()

    def _save(self):
        self._base._save()


class Configuration(AutoSavingDictionary, object):
    def __init__(self, config_type):
        resolver = Resolver.get()
        app_dirs = resolver(AppDirs)

        config_file_name = '{type}.json'.format(type=config_type)
        self._config_directory = app_dirs.user_config_dir
        self._config_path = os.path.join(self._config_directory, config_file_name)

        self._config = self.__load_config()
        super().__init__(self, self._config)

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
            json.dump(self._config, config_handle)