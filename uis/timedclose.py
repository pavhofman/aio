from threading import Timer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uis.webapp import WebApp

# the container gets closed after TIMEOUT of no activity
TIMEOUT = 2


class TimedClose:
    def __init__(self, app: 'WebApp', timeout=TIMEOUT):
        self._timeout = timeout
        self._app = app
        self._timer = None

    def activateTimer(self):
        if self._timer is None:
            self._startTimer()
        else:
            if self._timer.is_alive():
                # cancel and reschedule
                self._closeTimer()
                # new timer
                self._startTimer()

    def _startTimer(self):
        self._timer = Timer(self._timeout, self._timerFinished)
        self._timer.setDaemon(True)

        self._timer.start()

    def _closeTimer(self):
        self._timer.cancel()
        self._timer.join()

    def _timerFinished(self):
        # just showing the main screen
        self._timer = None
        self._app.showPrevFSContainer()
