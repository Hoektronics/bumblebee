from distutils.core import setup

import sys
from setuptools import find_packages
if sys.version_info > (3,):
    from setuptools import setup
else:
    from distutils.core import setup

NAME = "bqclient"
DESCRIPTION = "BotQueue's client bumblebee"
URL = "http://github.com/Hoektronics/bumblebee/"

PACKAGES = ["bumblebee", "bumblebee.drivers"]
PKG_DATA = {"bumblebee":["config-dist.json","imagesnap"]}
DEPENDS = ["git://github.com/makerbot/pyserial#egg=pyserial"]
REQUIRES = ["Pygments", "pyserial", "requests-oauth", "autoupgrade"]
EXCLUDES = ["pydoc"]

setup(name=NAME,
      author="Zach 'Hoeken' Smith",
      author_email="hoeken@gmail.com",
      maintainer="Justin Nesselrotte",
      maintainer_email="jnesselr@harding.edu",
      version='0.5.0',
      url=URL,
      packages=PACKAGES,
      entry_points={
         "console_scripts":["bumblebee = bumblebee.app:main"]
      },
      dependency_links=DEPENDS,
      install_requires=REQUIRES,
      package_data=PKG_DATA
     )

