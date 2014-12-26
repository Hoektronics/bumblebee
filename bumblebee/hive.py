import hashlib
import json
import logging
import logging.handlers
import os
import pprint
import shutil
import sys
import tarfile
import tempfile
from threading import Thread
import time
import urllib2

from bumblebee import drivers


class BeeConfig():
    def __init__(self):
        self.data = []
        self.loaded = False
        self.path = os.path.dirname(os.path.realpath(__file__)) + os.sep + "config.json"

    def get(self):
        if not self.loaded:
            self.load()
        return self.data

    def load(self):
        try:
            if not os.path.exists(self.path):
                # Move the old config?
                if os.path.exists("config.json"):
                    shutil.move("config.json", self.path)
                else:
                    config_dist = os.path.dirname(os.path.realpath(__file__)) + os.sep + "config-dist.json"
                    shutil.copy(config_dist, self.path)
            f = open(self.path, "r")
            self.data = json.load(f)
            f.close()

            return f
        except ValueError as e:
            print("Error parsing config file: %s" % e)
            raise RuntimeError("Error parsing config file: %s" % e)

    def save(self, data):
        f = open(self.path, "w")
        f.write(json.dumps(data, indent=2))
        f.close()
        self.data = data


class URLFile():
    def __init__(self, filedata):
        self.global_config = config.get()
        self.log = logging.getLogger('botqueue')

        # init our local variables.
        self.remotefile = filedata
        self.cacheHit = False
        self.localPath = False
        self.localFile = False
        self.localSize = 0
        self.progress = 0
        self.cacheDir = False
        self.cacheDir = getCacheDirectory()

    def load(self):
        self.prepareLocalFile()
        Thread(target=self.downloadFile).start()

    def getProgress(self):
        return self.progress

    # open our local file for writing.
    def prepareLocalFile(self):
        self.cacheHit = False
        try:
            self.localPath = self.cacheDir + self.remotefile['md5'] + "-" + os.path.basename(self.remotefile['name'])
            if os.path.exists(self.localPath):
                myhash = md5sumfile(self.localPath)
                if myhash != self.remotefile['md5']:
                    os.unlink(self.localPath)
                    self.log.warning(
                        "Existing file found: hashes did not match! %s != %s" % (myhash, self.remotefile['md5']))
                else:
                    self.cacheHit = True
                    self.localSize = os.path.getsize(self.localPath)
                    self.localFile = open(self.localPath, "rb")
                    self.progress = 100
            #  okay, should we open it for writing?
            if not os.path.exists(self.localPath):
                self.localFile = open(self.localPath, "w+b")
        except Exception:
            self.localFile = tempfile.NamedTemporaryFile()
            self.localPath = self.localFile.name

    #  download our job and make sure its cool
    def downloadFile(self):
        #  do we need to download it?
        if not self.cacheHit:
            while 1:
                try:
                    #  download our file.
                    self.log.info("Downloading %s to %s" % (self.remotefile['url'], self.localPath))
                    urlFile = self.openUrl(self.remotefile['url'])
                    chunk = 4096
                    md5 = hashlib.md5()
                    self.localSize = 0
                    while 1:
                        data = urlFile.read(chunk)
                        if not data:
                            break
                        md5.update(data)
                        self.localFile.write(data)
                        self.localSize = self.localSize + len(data)
                        self.progress = float(self.localSize) / float(self.remotefile['size']) * 100

                    #  check our final md5 sum.
                    if md5.hexdigest() != self.remotefile['md5']:
                        self.log.error(
                            "Downloaded file hash did not match! %s != %s" % (md5.hexdigest(), self.remotefile['md5']))
                        os.unlink(self.localPath)
                        raise Exception()
                    else:
                        self.progress = 100
                        self.log.info("Download complete: %s" % self.remotefile['url'])
                        self.localFile.seek(0)
                        return
                except Exception as ex:
                    self.log.exception(ex)
                    self.localFile.seek(0)
                    time.sleep(5)
        else:
            self.localFile.seek(0)
            self.log.info("Using cached file %s" % self.localPath)

    def openUrl(self, url):
        request = urllib2.Request(url)
        #  request.add_header('User-agent', 'Chrome XXX')
        urlfile = urllib2.urlopen(request)

        return urlfile


class Object(object):
    pass


def md5sumfile(filename, block_size=2 ** 18):
    md5 = hashlib.md5()
    f = open(filename, "rb")
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.close()
    return md5.hexdigest()


def getCacheDirectory():
    realPath = os.path.dirname(os.path.realpath(__file__))
    cacheDir = "%s%scache%s" % (realPath, os.sep, os.sep)

    # make it if it doesn't exist.
    if not os.path.isdir(cacheDir):
        os.mkdir(cacheDir)

    return cacheDir

def getImageDirectory(filename):
    realPath = os.path.dirname(os.path.realpath(__file__))
    imageDir = "%s%simages" % (realPath, os.sep)

    # make it if it doesn't exist.
    if not os.path.isdir(imageDir):
        os.mkdir(imageDir)

    path = "%s%s%s" % (imageDir, os.sep, filename)
    return path


def determineOS():
    if sys.platform.startswith('darwin'):
        return "osx"
    elif sys.platform.startswith('linux'):
        if os.uname()[4].startswith('arm'):
            return "raspberrypi"
        else:
            return "linux"
    elif sys.platform.startswith('win'):
        return "win"
    else:
        return "unknown"


def scanBots():
    driver_names = ['printcoredriver']
    bots = {}
    for name in driver_names:
        module_name = 'bumblebee.drivers.' + name
        __import__(module_name)
        found = getattr(drivers, name).scanPorts()
        if found:
            bots[name] = found

    return bots


def jsonNormalize(input):
    return json.loads(json.dumps(input))


def convertToString(input):
    result = input
    if isinstance(input, dict):
        result = {}
        for key, value in input.iteritems():
            result[convertToString(key)] = convertToString(value)
    elif isinstance(input, list):
        result = []
        for element in input:
            result.append(convertToString(element))
    elif isinstance(input, unicode):
        result = input.encode('utf-8')
    return result

def getLogPath():
    return os.path.dirname(os.path.realpath(__file__)) + os.sep + 'info.log'

def loadLogger():
    # create logger with 'spam_application'
    logger = logging.getLogger('botqueue')
    logger.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

    # create file handler which logs even debug messages (max 25mb)
    log_file = getLogPath()
    fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=26214400, backupCount = 3)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # create console handler with a higher log level
    # ch = logging.StreamHandler()
    #  ch.setLevel(logging.WARNING)
    #  ch.setFormatter(formatter)
    #  logger.addHandler(ch)

def getEngine(engine_name,
            type=None,
            repo=None):
    log = logging.getLogger('botqueue')
    
    engines = os.path.dirname(os.path.realpath(__file__))
    engines = engines + os.sep + "engines" + os.sep + type
    if not os.path.exists(os.path.abspath(engines)):
        os.makedirs(os.path.abspath(engines))
    engine_path = engines + os.sep + engine_name
    engine_path = os.path.abspath(engine_path)

    if os.path.exists(engine_path):
        return engine_path

    log.info("Downloading %s from %s to %s" % (engine_name, repo, engine_path))
    from subprocess import call
    log_stream = open(os.devnull, 'w')
    call(['git', 'clone', repo, engine_path], stdout=log_stream, stderr=log_stream)
    log.info("Downloading %s finished" % engine_name)
    return engine_path

def downloadSlicer(engine_path, engine_type, installPath):
    myos = determineOS()
    log = logging.getLogger('botqueue')
    tarFileName = None

    try:
        # Is it already installed?
        if not os.path.exists(installPath):
            user = 'Hoektronics'
            repo = 'engines'
            url = "https://github.com/%s/%s/archive/%s-%s.tar.gz" % (user, repo, myos, engine_path)
            log.info("Downloading %s from %s" % (engine_path, url))
            tarName = "%s-%s-%s" % (repo, myos, engine_path)
            log.info("Extracting to %s" % (installPath))
            if not os.path.exists(installPath):
                os.makedirs(installPath)

            tarFileName = "%s.tar.gz" % tarName
            download(url, tarFileName)

            myTarFile = tarfile.open(name=tarFileName)
            myTarFile.extractall(path=installPath)
            myTarFile.close()
            log.debug("Reading manifest")
            manifestFile = "%s/%s/manifest.json" % (installPath, tarName)
            manifest = json.load(open(manifestFile, 'r'))
            os.remove(manifestFile)
            dirName = manifest['directory']
            slicePath = "%s/%s/%s" % (installPath, dirName, manifest['path'])

            if (manifest['category'] != engine_type):
                raise Exception(
                    "%s was type %s not the expected %s" % (engine_path, manifest['category'], engine_type))
            os.renames("%s/%s" % (installPath, tarName), "%s/%s" % (installPath, dirName))

            log.debug(slicePath)
            # Double check everything was installed
            if not os.path.exists(slicePath):
                raise Exception("Something went wrong during installation")

            log.info("%s installed" % engine_path)

            return slicePath

    except Exception as ex:
        log.debug(ex)
        return None
    finally:
        if tarFileName is not None:
            os.remove(tarFileName)

def download(url, localFileName):
    localFile = open(localFileName, 'wb')
    request = urllib2.Request(url)
    urlFile = urllib2.urlopen(request)
    chunk = 4096

    while 1:
        data = urlFile.read(chunk)
        if not data:
            break
        localFile.write(data)
    localFile.close()

config = BeeConfig()
debug = pprint.PrettyPrinter(indent=4)
