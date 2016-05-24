import logging
import subprocess
import tempfile
import time
from distutils.spawn import find_executable

import os
import re
from bumblebee import hive
from bumblebee.events import CameraEvent
from bumblebee.RepeatedTimer import RepeatedTimer
from bumblebee.auto_deleted_file import AutoDeletedFile


class CameraControl:
    def __init__(self):
        self.log = logging.getLogger("botqueue")

    def get_cameras(self):
        return {}

    def take_picture(self, device, output):
        pass

    def _run_picture_command(self, command):
        output_log = ""
        error_log = ""
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        while p.poll() is None:
            output = p.stdout.readline()
            if output:
                output_log = output_log + output

            time.sleep(0.1)

        # get any last lines of output
        output = p.stdout.readline()
        while output:
            output_log = output_log + output
            output = p.stdout.readline()

        # get our errors (if any)
        error = p.stderr.readline()
        while error:
            self.log.error("Webcam: %s" % error.strip())
            error_log = error_log + error
            error = p.stderr.readline()

        # did we get errors?
        if error_log or p.returncode > 0:
            self.log.error("Errors detected.  Bailing.")
            return False
        else:
            return True


class CameraControlLinux(CameraControl):
    def get_cameras(self):
        if find_executable("uvcdynctrl") is None:
            return {}

        command = "uvcdynctrl -l -v"

        returned = subprocess.check_output(command, shell=True)
        lines = returned.rstrip().split('\n')

        devices = {}
        for line in lines:
            matches = re.findall("(video\\d+)[ ]+(.*) \\[(.+), (.+)\\]", line)

            # todo make this better
            if matches:
                matched_camera = matches[0]
                camera_id = matched_camera[3]
                camera = {"id": camera_id, "name": matched_camera[1], "device": "/dev/" + matched_camera[0]}
                devices[camera_id] = camera

        return devices

    def take_picture(self, device, output):
        command = "exec /usr/bin/fswebcam" \
                  " -q --jpeg 60 -d '%s'" \
                  " -r 640x480 '%s'" % (
                      device,
                      output
                  )

        return self._run_picture_command(command)


class CameraControlOSX(CameraControl):
    def get_cameras(self):
        command = os.path.dirname(os.path.realpath(__file__)) + os.sep + "imagesnap -l"

        returned = subprocess.check_output(command, shell=True)
        lines = returned.rstrip().split('\n')

        devices = {}
        if len(lines) > 1:
            for line in lines[1:]:
                camera = {"id": line, "name": line, "device": line}
                devices[line] = camera

        return devices

    def take_picture(self, device, output):
        imagesnap = os.path.dirname(os.path.realpath(__file__)) + os.sep + "imagesnap"
        command = "%s -q -d '%s' -w 2.0 '%s' && " \
                  "sips --resampleWidth 640" \
                  " --padToHeightWidth 480 640" \
                  " --padColor FFFFFF -s formatOptions 60%% '%s' 2>/dev/null" % (
                      imagesnap,
                      device,
                      output,
                      output
                  )

        return self._run_picture_command(command)


class CameraControlRaspberryPi(CameraControlLinux):
    def get_cameras(self):
        devices = CameraControlLinux.get_cameras(self)

        try:
            import picamera

            with picamera.PiCamera() as camera:
                line = "Rasberry Pi Camera"
                devices[line] = {"id": line, "name": line, "device": line}
                camera.close()
        except ImportError:
            pass

        return devices

    def take_picture(self, device, output):
        if device == "Rasberry Pi Camera":
            import picamera

            try:
                with picamera.PiCamera() as camera:
                    camera.capture(output, resize=(640, 480))
                    camera.close()
                    return True
            except picamera.exc.PiCameraError:
                return False
        else:
            return CameraControlLinux.take_picture(self, device, output)


class CameraController(object):
    def __init__(self):
        my_os = hive.determineOS()
        if my_os == "os":
            self._camera_control = CameraControlOSX()
        elif my_os == "linux":
            self._camera_control = CameraControlLinux()
        elif my_os == "raspberrypi":
            self._camera_control = CameraControlRaspberryPi()
        else:
            self._camera_control = CameraControl()

        self.cameras = {}
        self._timer = None

    def start(self):
        self._timer = RepeatedTimer(60, self._update)

    def _update(self):
        self._update_cameras()
        self._take_pictures()

    def _update_cameras(self):
        new_cameras = self._camera_control.get_cameras()
        if new_cameras is None:
            return

        for key, camera in new_cameras.items():
            if key not in self.cameras:
                CameraEvent.CameraAdded(camera).fire()

        for key, camera in self.cameras.items():
            if key not in new_cameras:
                CameraEvent.CameraRemoved(camera).fire()

        self.cameras = new_cameras

    def _take_pictures(self):
        for key, camera in self.cameras.items():
            camera_file_output = tempfile.NamedTemporaryFile(delete=False, suffix="jpg")
            camera_file_output.close()

            self._camera_control.take_picture(camera["device"], camera_file_output.name)

            # Emit that a new picture has been taken
            my_file = AutoDeletedFile(camera_file_output.name)
            CameraEvent.PictureTaken(camera, my_file).fire()


_controller = CameraController()


def start():
    _controller.start()
