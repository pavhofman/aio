import abc
import logging
from queue import Queue
from threading import Thread, Event, Lock
from typing import Optional

from common.mathutils import roundToInt
from sources.mpv import MPVCommandError
from sources.mympv import MyMPV
# global MPV for all sources
from sources.playbackstatus import PlaybackStatus

# MPV property with time position of the current track
SKIP_SECS = 10
TIME_POS_PROPERTY = "playback-time"

TIME_POS_READ_INTERVAL = 1
mpv = None  # type: Optional[MyMPV]
controlLock = Lock()


class UsesMPV(abc.ABC):
    def __init__(self, monitorTime: bool) -> None:
        super().__init__()
        self._monitorTime = monitorTime
        self._initTimePosTimer()
        # cached value
        self.__duration = None

    def _initTimePosTimer(self):
        if self._monitorTime:
            self._timePosTimer = TimePosTimer(self.timePosWasChanged, owner=self)

    def reInit(self):
        self._acquireMPV()
        self._initTimePosTimer()

    def _isPaused(self) -> bool:
        status = self._getMPV().get_property("pause")
        return status

    def _isIdle(self) -> bool:
        status = self._getMPV().get_property("idle")
        return status

    def _determinePlaybackStatus(self) -> PlaybackStatus:
        if self._isIdle():
            return PlaybackStatus.STOPPED
        else:
            if self._isPaused():
                return PlaybackStatus.PAUSED
            else:
                return PlaybackStatus.PLAYING

    def _changePlaybackStatusTo(self, newStatus: PlaybackStatus):
        if newStatus == PlaybackStatus.STOPPED:
            self._getMPV().stop()
            if self._monitorTime:
                self._timePosTimer.disable()
        elif newStatus == PlaybackStatus.PLAYING:
            self._getMPV().play()
        elif newStatus == PlaybackStatus.PAUSED:
            self._getMPV().pause()

    def _skipForward(self):
        self.__skipSecs(SKIP_SECS)

    def _skipBackward(self):
        self.__skipSecs(-1 * SKIP_SECS)

    def __skipSecs(self, skipSecs: int):
        if self._monitorTime:
            timePos = self._getTimePosition()
            if timePos is not None:
                newTimePos = timePos + skipSecs
                if newTimePos < 0:
                    newTimePos = 0
                self._getMPV().set_property(TIME_POS_PROPERTY, newTimePos)

    def _getTimePosition(self) -> Optional[int]:
        try:
            timePosFloat = self._getMPV().get_property(TIME_POS_PROPERTY)
            return roundToInt(timePosFloat) if timePosFloat is not None else None
        except MPVCommandError:
            # not much we can do
            return None

    def _acquireMPV(self):
        global mpv
        global controlLock
        with controlLock:
            # closing any mpv if running
            if mpv is not None:
                mpv.stop()
                mpv = None
            # starting
            mpv = MyMPV(owner=self)

    def _releaseMPV(self):
        global mpv  # type: MyMPV
        global controlLock
        with controlLock:
            # stop if mpv is mine
            if mpv is not None and mpv.getOwner() == self:
                mpv.stop()
                mpv = None

    @staticmethod
    def _getMPV() -> MyMPV:
        global mpv
        return mpv

    def close(self):
        if self._monitorTime:
            self._timePosTimer.finish()
        self._releaseMPV()

    def _startPlayback(self, mpvPath: Optional[str] = None, chapter: Optional[int] = None) -> None:
        if mpvPath is not None:
            self._getMPV().command("loadfile", mpvPath, "replace")
        if chapter is not None:
            self._getMPV().set_property("chapter", chapter)
        # mpv can be paused, unpause
        self._getMPV().play()
        if self._monitorTime:
            self._timePosTimer.trigger()

    def _appendToPlayback(self, filePath: str):
        self._getMPV().command("loadfile", filePath, "append")

    def _getChapter(self) -> Optional[int]:
        """
        :return: current chapter of None if the property is not available
        """
        try:
            chapter = self._getMPV().get_property("chapter")
            return chapter
        except MPVCommandError:
            return None

    @abc.abstractmethod
    def chapterWasChanged(self, chapter: Optional[int]) -> None:
        pass

    @abc.abstractmethod
    def metadataWasChanged(self, metadata: dict):
        pass

    def pauseWasChanged(self, pause: bool):
        if self._monitorTime:
            if pause:
                self._timePosTimer.disable()
            else:
                self._timePosTimer.trigger()

    def idleWasChanged(self, idle: bool):
        if self._monitorTime and idle:
            self._timePosTimer.disable()

    @abc.abstractmethod
    def _audioParamsWereChanged(self, params: dict):
        pass

    def _resetTimePosTimer(self):
        if self._monitorTime:
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
    def timePosWasChanged(self, timePosFromStart: int):
        pass

    @abc.abstractmethod
    def pathWasChanged(self, mpvPath: str):
        pass


class TimePosTimer(Thread):
    def __init__(self, callbackFn, owner: 'UsesMPV'):
        Thread.__init__(self)
        self._owner = owner
        self._callbackFn = callbackFn
        self._finishEvent = Event()
        self._triggerEvent = Event()
        self._enabled = False
        self._queue = Queue()
        self.start()

    def run(self):
        timeAdj = 0  # type: float
        while not self._finishEvent.is_set():
            # the timer is either triggered - run immediately, or waits TIME_POS_READ_INTERVAL
            sleep = TIME_POS_READ_INTERVAL + timeAdj
            self._triggerEvent.wait(timeout=sleep)
            if self._enabled:
                try:
                    timeAdj = self.watchTimePos(timeAdj)
                except Exception as e:
                    logging.debug(str(e))
            # reset the trigger event to wait the TIME_POS_READ_INTERVAL in next cycle
            self._triggerEvent.clear()

    def watchTimePos(self, timeAdj) -> float:
        myMpv = self._getMPV()
        if myMpv is not None:
            myMpv.register_property_callback(TIME_POS_PROPERTY, self.timePosCallback)
            timePos = self._queue.get()  # type: float
            myMpv.unregister_property_callback(TIME_POS_PROPERTY, self.timePosCallback)
            posInt = roundToInt(timePos)
            timeAdj = posInt - timePos
            # print("TimePos: " + str(timePos) + "; posInt: " + str(posInt) + "; timeAdj: " + str(timeAdj))
            self._callbackFn(posInt)
        return timeAdj

    def finish(self):
        self._finishEvent.set()

    def disable(self):
        self._enabled = False

    def trigger(self):
        self._enabled = True
        self._triggerEvent.set()

    def _getMPV(self) -> Optional[MyMPV]:
        global mpv
        if mpv is not None and mpv.getOwner() == self._owner:
            return mpv
        else:
            return None

    def timePosCallback(self, timePos: float):
        if timePos is not None:
            self._queue.put(timePos)
