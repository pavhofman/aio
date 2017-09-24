from threading import Lock, Timer


class PeriodicTask(object):
    """
    A periodic task running in threading.Timers
    """

    def __init__(self, interval: float, function):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self._stopped = True
        self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function()

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()
