import threading

class RestartableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)
    def clone(self):
        return RestartableThread(*self.args, **self.kwargs)