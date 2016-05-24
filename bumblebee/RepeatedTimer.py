from threading import Timer


class RepeatedTimer(object):
    def __init__(self, interval, function):
        self._interval = interval
        self._function = function
        self._timer = None
        self.start()

    def start(self):
        self._function()
        self._timer = Timer(self._interval, self.start)
        self._timer.daemon = True
        self._timer.start()

    def stop(self):
        if self._timer is not None:
            self._timer.cancel()
