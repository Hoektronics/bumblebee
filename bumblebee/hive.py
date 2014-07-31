import hashlib
import json
import logging
import os
import pprint
import shutil
import sys
import tempfile
from threading import Thread
import time
import urllib2

from bumblebee import drivers


class BeeConfig():
    def __init__(self):
        self.data = []
        self.loaded = False

    def get(self):
        if not self.loaded:
            self.load()
        return self.data

    def load(self):
        try:
            if not os.path.exists("config.json"):
                config_dist = os.path.dirname(os.path.realpath(__file__)) + os.sep + "config-dist.json"
                shutil.copy(config_dist, "config.json")
            f = open("config.json", "r")
            self.data = json.load(f)
            f.close()

            return f
        except ValueError as e:
            print("Error parsing config file: %s" % e)
            raise RuntimeError("Error parsing config file: %s" % e)

    def save(self, data):
        f = open("config.json", "w")
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
                    self.localFile = open(self.localPath, "r")
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
    global_config = config.get()
    if 'cache_directory' in global_config:
        cacheDir = global_config['cache_directory']
    else:
        realPath = os.path.dirname(os.path.realpath(__file__))
        cacheDir = "%s/cache/" % (realPath)

    # make it if it doesn't exist.
    if not os.path.isdir(cacheDir):
        os.mkdir(cacheDir)

    return cacheDir


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
        module_name = 'drivers.' + name
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


def loadLogger():
    # create logger with 'spam_application'
    logger = logging.getLogger('botqueue')
    logger.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

    # create file handler which logs even debug messages
    fh = logging.FileHandler('info.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # create console handler with a higher log level
    # ch = logging.StreamHandler()
    #  ch.setLevel(logging.WARNING)
    #  ch.setFormatter(formatter)
    #  logger.addHandler(ch)


config = BeeConfig()
debug = pprint.PrettyPrinter(indent=4)
