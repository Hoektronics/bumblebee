class ApiManager(object):
    def __init__(self):
        self.handlers = []
        self.tasks = []
        self._start_called = False

    def add_handler(self, handler):
        self.handlers.append(handler)

        handler_tasks = handler.tasks()
        self.tasks.extend(handler_tasks)

        if self._start_called:
            for task in handler_tasks:
                task.start()

    def start(self):
        for task in self.tasks:
            task.start()
        self._start_called = True
