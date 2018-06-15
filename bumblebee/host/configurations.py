from bumblebee.host.framework.configuration import Configuration


class HostConfiguration(Configuration):
    def __init__(self, app_dirs):
        super(HostConfiguration, self).__init__(app_dirs, 'host')

    @staticmethod
    def _default_config():
        return {
            'server': 'https://botqueue.com/'
        }