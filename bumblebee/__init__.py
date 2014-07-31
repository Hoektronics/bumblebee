__all__ = ["app", "botqueueapi", "camera_control", "ginsu", "hive", "stacktracer", "workerbee"]

import os
from os.path import expanduser

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

print "Version string"
print __version__
print "Done"
