import os

from appdirs import AppDirs
import requests


class Downloader(object):
    def __init__(self,
                 app_dirs: AppDirs
                 ):
        self.app_dirs = app_dirs

    def download(self, url):
        downloads = os.path.join(self.app_dirs.user_data_dir, "downloads")
        os.makedirs(downloads, exist_ok=True)

        file_name = os.path.join(downloads, "file.gcode")

        with requests.get(url) as http_request:
            with open(file_name, 'wb') as fh:
                fh.write(http_request.content)

        print(f"{url} written to {file_name}")

        return file_name
