from distutils.spawn import find_executable
import logging
import os
import re
import subprocess
from threading import Lock
import time

from bumblebee import hive

mutex = Lock()


def __run_picture_command(command, log):
    outputLog = ""
    errorLog = ""
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # log.info("Webcam Capture started.")
    while p.poll() is None:
        output = p.stdout.readline()
        if output:
            # log.info("Webcam: %s" % output.strip())
            outputLog = outputLog + output

        time.sleep(0.5)

    # get any last lines of output
    output = p.stdout.readline()
    while output:
        outputLog = outputLog + output
        output = p.stdout.readline()

    # get our errors (if any)
    error = p.stderr.readline()
    while error:
        log.error("Webcam: %s" % error.strip())
        errorLog = errorLog + error
        error = p.stderr.readline()
    # did we get errors?
    if (errorLog or p.returncode > 0):
        log.error("Errors detected.  Bailing.")
        return False
    else:
        return True


def takePicture(device, watermark=None, output="webcam.jpg", brightness=50, contrast=50):
    output = hive.getImageDirectory(output)
    with mutex:
        log = logging.getLogger('botqueue')

        try:
            # what os are we using
            myos = hive.determineOS()
            if myos == "osx":
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
                # log.info("Webcam Command: %s" % command)
                return __run_picture_command(command, log)
            elif myos == "raspberrypi" or myos == "linux":
                if device == "Rasberry Pi Camera":
                    import picamera

                    try:
                        with picamera.PiCamera() as camera:
                            camera.capture(output, resize=(640, 480))
                            camera.close()
                            return True
                    except picamera.exc.PiCameraError as ex:
                        # No need to log an exception here
                        return False
                else:
                    command = "exec /usr/bin/fswebcam" \
                              " -q --jpeg 60 -d '%s'" \
                              " -r 640x480 --title '%s'" \
                              " --set brightness=%s%%" \
                              " --set contrast=%s%% '%s'" % (
                                  device,
                                  watermark,
                                  brightness,
                                  contrast,
                                  output
                              )
                    # log.info("Webcam Command: %s" % command)
                    return __run_picture_command(command, log)
            else:
                raise Exception("Webcams are not supported on your OS (%s)." % myos)

        except Exception as ex:
            log.exception(ex)
            return False


def __scanCameraRaspi(cameras):
    __scanCameraLinux(cameras)
    return

    try:
        import picamera

        with picamera.PiCamera() as camera:
            line = "Rasberry Pi Camera"
            cameras.append({"id": line, "name": line, "device": line})
            camera.close()
    except ImportError:
        pass


def __scanCameraLinux(cameras):
    if (find_executable("uvcdynctrl") is None):
        return
    command = "uvcdynctrl -l -v"

    returned = subprocess.check_output(command, shell=True)
    lines = returned.rstrip().split('\n')

    for line in lines:
        matches = re.findall('(video\d+)[ ]+(.*) \[(.+), (.+)\]', line)
        # todo make this better
        if matches:
            camera = {"id": matches[0][3], "name": matches[0][1], "device": "/dev/" + matches[0][0]}
            cameras.append(camera)


def __scanCamerasOSX(cameras):
    command = os.path.dirname(os.path.realpath(__file__)) + os.sep + "imagesnap -l"

    returned = subprocess.check_output(command, shell=True)
    lines = returned.rstrip().split('\n')

    if len(lines) > 1:
        for line in lines[1:]:
            camera = {"id": line, "name": line, "device": line}
            cameras.append(camera)


def scanCameras():
    with mutex:
        cameras = []
        myos = hive.determineOS()
        if myos == "osx":
            __scanCamerasOSX(cameras)
        elif myos == "linux":
            __scanCameraLinux(cameras)
        elif myos == "raspberrypi":
            __scanCameraRaspi(cameras)

    return cameras
