__all__ = ["botqueueapi", "bumblebee", "camera_control", "ginsu", "hive", "stacktracer", "workerbee"]

import bumblebee
import os
from os.path import expanduser

def main():
  bee = bumblebee.BumbleBee()
  bee.main()

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

print "Version string"
print __version__
print "Done"

if __name__ == '__main__':
  main()
