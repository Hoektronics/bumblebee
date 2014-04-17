from esky import bdist_esky
import sys
from setuptools import find_packages
if sys.version_info > (3,):
    from setuptools import setup
else:
    from distutils.core import setup

NAME = "bumblebee"
VERSION = "0.5.0"
DESCRIPTION = "BotQueue's client bumblebee"
URL = "http://github.com/Hoektronics/bumblebee/"

PACKAGES = find_packages()
EXT_MODULES = []
PKG_DATA = {"bumblebee":["config-dist.json"]}
INCLUDES = ["requests", "serial"]
EXCLUDES = ["pydoc"]

setup(name=NAME,
      version=VERSION,
      author="Zach 'Hoeken' Smith",
      author_email="hoeken@gmail.com",
      maintainer="Justin Nesselrotte",
      maintainer_email="jnesselr@harding.edu",
      url=URL,
      packages=PACKAGES,
      entry_points={
         "console_scripts":["bumblebee = bumblbebee:main"]
      },
      ext_modules=EXT_MODULES,
      package_data=PKG_DATA,
      options = {"bdist_esky":{
            "includes":INCLUDES,
            "excludes":EXCLUDES
      }}
     )

