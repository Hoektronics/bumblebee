import os


class AutoDeletedFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def __del__(self):
        os.remove(self.file_path)
