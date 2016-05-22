import hashlib
import json
import shutil

import time

import appdirs
import os


class BeeConfig:
    def __init__(self):
        self.data = {}
        self.loaded = False

        self.config_dir = appdirs.user_config_dir("Bumblebee", "BotQueue")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        self.path = self.config_dir + os.sep + "config.json"

        self.setup_config_file()

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        del self.data[key]

    def load(self):
        try:
            f = open(self.path, "r")
            self.data = json.load(f)
            f.close()

            return f
        except ValueError as e:
            print("Error parsing config file: %s" % e)
            raise RuntimeError("Error parsing config file: %s" % e)

    def save(self):
        f = open(self.path, "w")
        f.write(json.dumps(self.data, indent=2))
        f.close()

    def automatically_move_config_file(self):
        if os.path.exists(self.path):
            return

        # Move it from the current directory to the current one
        if os.path.exists("config.json"):
            shutil.move("config.json", self.path)

        # Move it from the pip directory to the current one
        pip_config_path = os.path.dirname(os.path.realpath(__file__)) + os.sep + "config.json"
        if os.path.exists(pip_config_path):
            shutil.move(pip_config_path, self.path)

    def setup_config_file(self):
        self.automatically_move_config_file()

        if not os.path.exists(self.path):
            self.data = {
                'app_url': 'https://www.botqueue.com',
                'api': {
                    'authorize_url': 'https://www.botqueue.com/app/authorize',
                    'endpoint_url': 'https://www.botqueue.com/api/v1/endpoint'
                },
                'app': {
                    'consumer_key': '4b99f7bb861ad3fab5b3d4a189c81c0b893c043f',
                    'consumer_secret': 'c917f6ade3945e1acb9645dd1d7ee5d72993c6c9'
                }
            }
            self.save()

        self.load()
        self.migrate_configuration()

    def migrate_configuration(self):
        config_updated = False

        # check for default info.
        if 'app_url' not in self.data:
            self['app_url'] = "https://www.botqueue.com"
            config_updated = True

        # create a unique hash that will identify this computers requests
        if 'uid' not in self.data or len(self['uid']) != 40:
            self['uid'] = hashlib.sha1(str(time.time())).hexdigest()
            config_updated = True

        # slicing options moved to driver config
        if 'can_slice' in self.data:
            del self['can_slice']
            config_updated = True
        if config_updated:
            self.save()
