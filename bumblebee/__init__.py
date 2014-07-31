__all__ = ["app", "botqueueapi", "camera_control", "ginsu", "hive", "stacktracer", "workerbee"]

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions
