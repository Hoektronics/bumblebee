from esky import bdist_esky
from distutils.core import setup

import sys
from setuptools import find_packages
if sys.version_info > (3,):
    from setuptools import setup
else:
    from distutils.core import setup

NAME = "bumblebee"
DESCRIPTION = "BotQueue's client bumblebee"
URL = "http://github.com/Hoektronics/bumblebee/"

PACKAGES = ["bumblebee"]
EXT_MODULES = []
PKG_DATA = {"bumblebee":["config-dist.json"]}
INCLUDES = ["requests", "serial"]
EXCLUDES = ["pydoc"]
SCRIPTS = ["bumblebee/app.py"]
OPTIONS = {"bdist_esky": {
    "freezer_module":"py2app"
}}

setup(name=NAME,
      author="Zach 'Hoeken' Smith",
      author_email="hoeken@gmail.com",
      maintainer="Justin Nesselrotte",
      maintainer_email="jnesselr@harding.edu",
      url=URL,
      packages=PACKAGES,
      entry_points={
         "console_scripts":["bumblebee = bumblebee.app:main"]
      },
      scripts=SCRIPTS,
      ext_modules=EXT_MODULES,
      package_data=PKG_DATA,
      options=OPTIONS
     )

