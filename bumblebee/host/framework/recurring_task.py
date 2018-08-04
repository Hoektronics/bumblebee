from threading import Thread, Event


class RecurringTask(Thread):
    def __init__(self, interval, func):
        Thread.__init__(self)
        self.interval = interval
        self.function = func
        self.cancelled = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.cancelled.set()

    def run(self):
        while not self.cancelled.is_set():
            self.function()
            self.cancelled.wait(self.interval)