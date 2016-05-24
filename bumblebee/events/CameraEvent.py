from bumblebee.events import Event


class PictureTaken(Event):
    def __init__(self, camera, picture):
        self.camera = camera
        self.picture = picture


class CameraAdded(Event):
    def __init__(self, camera):
        self.camera = camera


class CameraRemoved(Event):
    def __init__(self, camera):
        self.camera = camera
