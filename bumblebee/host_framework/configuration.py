import appdirs
import json
import os


class Configuration(object):
    def __init__(self):
        self._config = {}


class HostConfiguration(Configuration):
    def __init__(self, app_name):
        super(HostConfiguration, self).__init__()
        self.app_name = app_name
        self._config = self.__load_config(app_name)

    @staticmethod
    def __load_config(app_name):
        config_directory = appdirs.user_config_dir(app_name)
        host_config_path = os.path.join(config_directory, 'host.json')

        if os.path.exists(host_config_path):
            with open(host_config_path, 'rb') as host_config_handle:
                return json.dump(host_config_handle)
