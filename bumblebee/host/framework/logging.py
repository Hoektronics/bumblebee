import logging
import os

from appdirs import AppDirs


class HostLogging(object):
    def __init__(self,
                 app_dirs: AppDirs):
        os.makedirs(app_dirs.user_log_dir, exist_ok=True)
        self._host_log_path = os.path.join(app_dirs.user_log_dir, 'host.log')

    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.propagate = False
        logger.setLevel(logging.DEBUG)

        matching_file_handlers = [
            handler for handler in logger.handlers
            if isinstance(handler, logging.FileHandler) and handler.stream.name == self._host_log_path
        ]

        if not matching_file_handlers:
            file_handler = logging.FileHandler(self._host_log_path)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)

        return logger
