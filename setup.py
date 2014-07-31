import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'bumblebee/_version.py'
versioneer.versionfile_build = 'bumblebee/_version'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'bumblebee-'

import sys
from setuptools import find_packages
if sys.version_info > (3,):
    from setuptools import setup
else:
    from distutils.core import setup

NAME = "bumblebee"
DESCRIPTION = "BotQueue's client bumblebee"
URL = "http://github.com/Hoektronics/bumblebee/"

PACKAGES = find_packages()
EXT_MODULES = []
PKG_DATA = {"bumblebee":["config-dist.json"]}
INCLUDES = ["requests", "serial"]
EXCLUDES = ["pydoc"]

setup(name=NAME,
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      author="Zach 'Hoeken' Smith",
      author_email="hoeken@gmail.com",
      maintainer="Justin Nesselrotte",
      maintainer_email="jnesselr@harding.edu",
      url=URL,
      packages=PACKAGES,
      entry_points={
         "console_scripts":["bumblebee = bumblebee:main"]
      },
      ext_modules=EXT_MODULES,
      package_data=PKG_DATA
     )

