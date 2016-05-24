from __future__ import print_function
import json

from bumblebee import drivers
from bumblebee import bee_config
from bumblebee import botqueueapi
from bumblebee.RepeatedTimer import RepeatedTimer
from bumblebee.events import CameraEvent


class DeviceScanner(object):
    def __init__(self):
        self._last_scan_data = None
        self._bots = {}
        self._cameras = {}
        self._pictures = {}

        self.config = bee_config.BeeConfig()

        # load up our api
        self.api = botqueueapi.BotQueueAPI(self.config)

        self._timer = RepeatedTimer(60, self._scan_devices)

        CameraEvent.CameraAdded.then(self.on_camera_added)
        CameraEvent.CameraRemoved.then(self.on_camera_removed)
        CameraEvent.PictureTaken.then(self.on_picture_taken)

    def on_camera_added(self, event):
        camera = event.camera
        print("Camera added", camera)
        self._cameras[camera["device"]] = camera

    def on_camera_removed(self, event):
        camera = event.camera
        del self._cameras[camera["device"]]

    def on_picture_taken(self, event):
        camera = event.camera
        self._pictures[camera["device"]] = event.picture

    def _scan_devices(self):
        self._scan_bots()

        # look up our data
        data = {
            'bots': self._bots,
            'cameras': self._cameras.values()
        }

        scan_data = json.dumps(data)
        print(scan_data)
        print(len(self._cameras))

        if scan_data != self._last_scan_data or self._cameras:
            self._last_scan_data = scan_data

            self.api.sendDeviceScanResults(data, self._pictures.values())

    def _scan_bots(self):
        driver_names = ['printcoredriver']
        for name in driver_names:
            module_name = 'bumblebee.drivers.' + name
            __import__(module_name)
            found = getattr(drivers, name).scanPorts()
            self._bots[name] = found
