import abc
import decimal
from queue import Queue
from threading import Thread, Event
from typing import Optional

from sources.mpv import MPVCommandError
from sources.mympv import MyMPV
# global MPV for all sources
from sources.playbackstatus import PlaybackStatus

# MPV property with time position of the current track
TIME_POS_PROPERTY = "playback-time"

TIME_POS_READ_INTERVAL = 1
mpv = None  # type: Optional[MyMPV]


def roundToInt(timePos: float) -> int:
    return int(decimal.Decimal(timePos).quantize(decimal.Decimal(1),
                                                 rounding=decimal.ROUND_HALF_UP))


class UsesMPV(abc.ABC):
    def __init__(self) -> None:
        super().__init__()
        self._timePosTimer = TimePosTimer(self.timePosWasChanged)
        # cached value
        self.__duration = None

    def _isPaused(self) -> bool:
        status = self._getMPV().get_property("pause")
        return status

    def _isIdle(self) -> bool:
        status = self._getMPV().get_property("idle")
        return status

    def _determinePlayback(self) -> PlaybackStatus:
        if self._isIdle():
            return PlaybackStatus.STOPPED
        else:
            if self._isPaused():
                return PlaybackStatus.PAUSED
            else:
                return PlaybackStatus.PLAYING

    def _changePlaybackTo(self, playback: PlaybackStatus):
        if playback == PlaybackStatus.STOPPED:
            self._getMPV().stop()
            self._timePosTimer.disable()
        elif playback == PlaybackStatus.PLAYING:
            self._getMPV().play()
        elif playback == PlaybackStatus.PAUSED:
            self._getMPV().pause()

    def _acquireMPV(self):
        global mpv
        # closing any mpv, even if it belongs to another source
        if mpv is not None:
            mpv.close()
            # acquiring for myself
        mpv = MyMPV(self)

    def _releaseMPV(self):
        global mpv  # type: MyMPV
        if mpv is not None and mpv.source == self:
            mpv.close()

    @staticmethod
    def _getMPV() -> MyMPV:
        global mpv
        return mpv

    def close(self):
        self._timePosTimer.finish()

    def _startPlayback(self, filePath: str):
        self._getMPV().command("loadfile", filePath, "replace")
        self._timePosTimer.trigger()

    def _appendToPlayback(self, filePath: str):
        self._getMPV().command("loadfile", filePath, "append")

    @abc.abstractmethod
    def chapterWasChanged(self, chapter: int):
        pass

    @abc.abstractmethod
    def metadataWasChanged(self, metadata: dict):
        pass

    def pauseWasChanged(self, pause: bool):
        if pause:
            self._timePosTimer.disable()
        else:
            self._timePosTimer.trigger()

    def idleWasChanged(self, idle: bool):
        if idle:
            self._timePosTimer.disable()

    def pathWasChanged(self, filePath: str):
        self._timePosTimer.trigger()
        self.__duration = None

    def _getDuration(self) -> Optional[int]:
        if self.__duration is None:
            self.__duration = self._readDuration()
        return self.__duration

    def _readDuration(self):
        try:
            duration = self._getMPV().get_property("duration")
            return roundToInt(duration)
        except MPVCommandError:
            return None

    @abc.abstractmethod
    def timePosWasChanged(self, timePos: int):
        pass


class TimePosTimer(Thread):
    def __init__(self, callbackFn):
        Thread.__init__(self)
        self._callbackFn = callbackFn
        self._finishEvent = Event()
        self._triggerEvent = Event()
        self._enabled = False
        self._queue = Queue()
        self.start()

    def run(self):
        timeAdj = 0
        while not self._finishEvent.is_set():
            # the timer is either triggered - run immediately, or waits TIME_POS_READ_INTERVAL
            sleep = TIME_POS_READ_INTERVAL + timeAdj
            self._triggerEvent.wait(timeout=sleep)
            if self._enabled:
                self._getMPV().register_property_callback(TIME_POS_PROPERTY, self.timePosCallback)
                timePos = self._queue.get()
                self._getMPV().unregister_property_callback(TIME_POS_PROPERTY, self.timePosCallback)
                posInt = roundToInt(timePos)
                timeAdj = posInt - timePos
                self._callbackFn(posInt)
            # reset the trigger event to wait the TIME_POS_READ_INTERVAL in next cycle
            self._triggerEvent.clear()

    def finish(self):
        self._finishEvent.set()

    def disable(self):
        self._enabled = False

    def trigger(self):
        self._enabled = True
        self._triggerEvent.set()

    @staticmethod
    def _getMPV() -> MyMPV:
        global mpv
        return mpv

    def timePosCallback(self, timePos: float):
        if timePos is not None:
            self._queue.put(timePos)
