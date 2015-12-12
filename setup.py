import sys

import re
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
REQUIRES = ["Pygments", "pyserial", "requests-oauth", "beautifulsoup4", "makerbot-driver"]
EXCLUDES = ["pydoc"]

VERSIONFILE = "bumblebee/_version.py"
line = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__\s*=\s*['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, line, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)

setup(name=NAME,
      author="Zach 'Hoeken' Smith",
      author_email="hoeken@gmail.com",
      maintainer="Justin Nesselrotte",
      maintainer_email="jnesselr@harding.edu",
      description=DESCRIPTION,
      version=VERSION,
      url=URL,
      packages=PACKAGES,
      entry_points={
         "console_scripts":["bumblebee = bumblebee.__main__:main"]
      },
      dependency_links=DEPENDS,
      install_requires=REQUIRES,
      package_data=PKG_DATA
     )

