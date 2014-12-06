import json
import logging
import os
import re
import shutil
import signal
import stat
import subprocess
import tempfile
from threading import Thread, RLock
import time

from bumblebee import hive


class Ginsu():
    # A static lock for when other threads try to download a slicer
    downloadLock = RLock()

    def __init__(self, sliceFile, sliceJob):
        self.log = logging.getLogger('botqueue')
        self.sliceFile = sliceFile
        self.sliceJob = sliceJob
        self.slicer = None
        self.sliceThread = None
        self.sliceResult = False

    def isRunning(self):
        return self.slicer.isRunning()

    def stop(self):
        self.log.debug("Ginsu - stopping slice job.")
        if self.slicer is not None:
            self.slicer.stop()
        if self.sliceThread is not None:
            self.sliceThread.join(10)

    def getProgress(self):
        if self.slicer is not None:
            return self.slicer.getProgress()
        else:
            return 0

    def getResult(self):
        return self.sliceResult

    def slicerFactory(self):
        slice_config = self.sliceJob['slice_config']
        # todo: Make sure the engine exists
        slicer_name = slice_config['engine']['path']
        slicer = None
        if slicer_name.startswith('slic3r'):
            slicer = Slic3r(slice_config, self.sliceFile)
        elif slicer_name.startswith('cura'):
            slicer = Cura(slice_config, self.sliceFile)

        # getSlicerPath is called to verify the engine exists and
        # is available for this OS
        slicer.getSlicerPath()
        return slicer

    def slice(self):
        self.log.info("Starting slice.")
        self.slicer = self.slicerFactory()

        self.sliceThread = Thread(target=self.threadEntry).start()

    def threadEntry(self):
        self.sliceResult = self.slicer.slice()


class GenericSlicer(object):
    def __init__(self, config, slicefile):
        self.config = config
        self.log = logging.getLogger('botqueue')

        self.sliceFile = slicefile
        self.progress = 0
        self.running = True
        self.name = "GenericSlicer"

        self.prepareFiles()

    def stop(self):
        self.log.debug("Generic slicer stopped.")
        self.running = False

    def isRunning(self):
        return self.running

    def prepareFiles(self):
        pass

    def slice(self):
        pass

    def getProgress(self):
        return self.progress

class CommandLineSlicer(GenericSlicer):
    def __init__(self, config, slice_file):
        super(CommandLineSlicer, self).__init__(config, slice_file)
        self.name = "CommandLineSlicer"

    def getSlicerPath(self):
        # Have we already figured out where we are?
        if self.slicePath and os.path.exists(self.slicePath):
            return self.slicePath

        my_os = hive.determineOS()
        if my_os == "unknown":
            raise Exception("This engine is not supported on your OS.")

        # figure out where our path is.
        realPath = os.path.dirname(os.path.realpath(__file__))
        engine_type = self.config['engine']['type']
        engine_path = self.config['engine']['path']
        sliceEnginePath = "%s/engines/%s/%s" % (realPath, engine_type, engine_path)
        if not os.path.exists(sliceEnginePath):
            with Ginsu.downloadLock:
                self.slicePath = hive.downloadSlicer(engine_path, engine_type, sliceEnginePath)
                if self.slicePath is None:
                    raise Exception("The requested engine can't be installed.")
                else:
                    # Change permissions
                    st = os.stat(self.slicePath)
                    os.chmod(self.slicePath, st.st_mode | stat.S_IEXEC)
        else:
            user = 'Hoektronics'
            repo = 'engines'
            url = "https://raw.github.com/%s/%s/%s-%s/manifest.json" % (user, repo, my_os, engine_path)
            manifestFile = "%s-%s-manifest.json"
            hive.download(url, manifestFile)
            manifest = json.load(open(manifestFile, 'r'))
            os.remove(manifestFile)
            dirName = manifest['directory']
            self.slicePath = "%s/%s/%s" % (sliceEnginePath, dirName, manifest['path'])
            if not (os.path.exists(self.slicePath)):
                self.log.debug("Cleaning up bad installation")
                shutil.rmtree(sliceEnginePath)
                return self.getSlicerPath()

        return self.slicePath

    def prepareFiles(self):
        self.configFile = tempfile.NamedTemporaryFile(delete=False)
        self.configFile.write(self.config['config_data'])
        self.configFile.flush()
        self.log.debug("Config file: %s" % self.configFile.name)

        self.outFile = tempfile.NamedTemporaryFile(delete=False)
        self.log.debug("Output file: %s" % self.outFile.name)

    def run_process(self, command, output_file, cwd, output_callback):
        try:
            if hive.determineOS() != "win":
                command = "exec " + command
            self.log.info("Slice Command: %s" % command)

            outputLog = ""
            errorLog = ""

            # this starts our thread to slice the model into gcode
            self.p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
            self.log.info("%s started." % self.name)
            while self.p.poll() is None:
                output = self.p.stdout.readline()
                if output:
                    self.log.info("%s: %s" % (self.name, output.strip()))
                    outputLog = outputLog + output
                    output_callback(output)

                time.sleep(0.1)

                # did we get cancelled?
                if not self.running:
                    self.p.terminate()
                    self.p.kill()
                    return

                    # this code does not work for some reason and ends up blocking the loop
                    # until program exits if there is no errors
                    # this is a bummer, because we can't get realtime error logging.  :(
                    # err = self.p.stderr.readline().strip()
                    #         if err:
                    #           self.log.error("Slic3r: %s" % error)
                    #           errorLog = errorLog + err

            # get any last lines of output
            output = self.p.stdout.readline()
            while output:
                self.log.debug("%s: %s" % (self.name, output.strip()))
                outputLog = outputLog + output
                output_callback(output)
                output = self.p.stdout.readline()

            # get our errors (if any)
            error = self.p.stderr.readline()
            while error:
                self.log.error("%s: %s" % (self.name, error.strip()))
                errorLog = errorLog + error
                error = self.p.stderr.readline()

            # give us 1 second for the main loop to pull in our finished status.
            time.sleep(1)

            # save all our results to an object
            sushi = hive.Object
            sushi.output_file = output_file.name
            sushi.output_log = outputLog
            sushi.error_log = errorLog

            # did we get errors?
            if errorLog:
                sushi.status = "pending"
            # unknown return code... failure
            elif self.p.returncode > 0:
                sushi.status = "failure"
                self.log.error("Program returned code %s" % self.p.returncode)
            else:
                sushi.status = "complete"

            # okay, we're done!
            self.running = False

            return sushi
        except Exception as ex:
            self.log.exception(ex)

    def kill(self, process):
        self.log.debug("%s slicer stopped." % self.name)
        if process is not None:
            try:
                self.log.info("Killing %s process." % self.name)
                # self.p.terminate()
                os.kill(process.pid, signal.SIGTERM)
                t = 5  # max wait time in secs
                while process.poll() < 0:
                    if t > 0.5:
                        t -= 0.25
                        time.sleep(0.25)
                    else:  # still there, force kill
                        os.kill(process.pid, signal.SIGKILL)
                        time.sleep(0.5)
                process.poll()  # final try
            except OSError:
                # self.log.info("Kill exception: %s" % ex)
                pass  # successfully killed process
            self.log.info("Slicer killed.")
        self.running = False


class Cura(CommandLineSlicer):
    def __init__(self, config, slice_file):
        super(Cura, self).__init__(config, slice_file)
        self.name = "Cura"
        self.slicePath = None

        self.p = None

    def stop(self):
        self.kill(self.p)

    def checkProgress(self, line):
        self.log.debug(line)
        if not self.running:
            self.progress = 100
        else:
            self.progress = 0

    def slice(self):
        slicer_path = self.getSlicerPath()
        # create our command to do the slicing
        command = "%s -i %s -o %s -s %s" % (
            slicer_path,
            self.configFile.name,
            self.outFile.name,
            self.sliceFile.localPath
        )

        cwd = os.path.dirname(slicer_path)

        return self.run_process(command, self.outFile, cwd, self.checkProgress)


class Slic3r(CommandLineSlicer):
    def __init__(self, config, slice_file):
        super(Slic3r, self).__init__(config, slice_file)
        self.name = "Slic3r"
        self.slicePath = None

        self.p = None

        # our regexes
        self.regex = {         
            re.compile('Processing input file'): 5,
            re.compile('Processing triangulated mesh'): 10,
            re.compile('Generating perimeters'): 20,
            re.compile('Detecting solid surfaces'): 30,
            re.compile('Preparing infill surfaces'): 40,
            re.compile('Detect bridges'): 50,
            re.compile('Generating horizontal shells'): 60,
            re.compile('Combining infill'): 70,
            re.compile('Infilling layers'): 80,
            re.compile('Generating skirt'): 90,
            re.compile('Exporting G-code to'): 100
        }

    def stop(self):
        self.kill(self.p)

    def checkProgress(self, line):
        for key, value in self.regex.iteritems():
            if key.search(line):
                self.progress = value

    def slice(self):
        slicer_path = self.getSlicerPath()
        # create our command to do the slicing
        command = "%s --load %s --output %s %s" % (
            slicer_path,
            self.configFile.name,
            self.outFile.name,
            self.sliceFile.localPath
        )
        cwd = os.path.dirname(slicer_path)

        return self.run_process(command, self.outFile, cwd, self.checkProgress)
