import logging

from bumblebee.RepeatedTimer import RepeatedTimer
from bumblebee.events import BotEvent

try:
    from bumblebee import autoupgrade as auto_upgrade

except ImportError:
    auto_upgrade = None


class UpgradeChecker(object):
    def __init__(self):
        if auto_upgrade is not None:
            self.app = auto_upgrade.AutoUpgrade("bqclient", "https://pypi.python.org/simple")
        else:
            self.app = None

        self._timer = RepeatedTimer(300, self.upgrade_check)
        self._can_upgrade = False
        self._log = logging.getLogger('botqueue')

    def upgrade_check(self):
        self._can_upgrade = self.app is not None and self.app.check()