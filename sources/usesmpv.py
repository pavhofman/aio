import abc
from threading import Thread, Event
from typing import Optional

from sources.mpv import MPVCommandError
from sources.mympv import MyMPV
# global MPV for all sources
from sources.playbackstatus import PlaybackStatus

TIME_INTERVAL = 1
mpv = None  # type: Optional[MyMPV]


class UsesMPV(abc.ABC):
    def __init__(self) -> None:
        super().__init__()
        self._timerFinishFlag = Event()
        self._timerEnableFlag = Event()
        self._timePosTimer = RepeatingTimer(self._timerEnableFlag, self._timerFinishFlag, self.sendTimePos)

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

    def _getMPV(self) -> MyMPV:
        global mpv
        return mpv

    def close(self):
        self._timerFinishFlag.set()

    def _startPlayback(self):
        self._getMPV().play()
        self._timerEnableFlag.set()

    @abc.abstractmethod
    def chapterWasChanged(self, chapter: int):
        pass

    @abc.abstractmethod
    def metadataWasChanged(self, metadata: dict):
        pass

    def pauseWasChanged(self, pause: bool):
        if pause:
            self._timerEnableFlag.clear()
        else:
            self._timerEnableFlag.set()

    @abc.abstractmethod
    def pathWasChanged(self, filePath: str):
        pass

    @abc.abstractmethod
    def timePosWasChanged(self, timePos: float):
        pass

    def sendTimePos(self) -> None:
        try:
            timePos = self._getMPV().get_property("playback-time")  # type: float
            if timePos is not None:
                self.timePosWasChanged(timePos)
        except MPVCommandError:
            pass


class RepeatingTimer(Thread):
    def __init__(self, enableEvent: Event, finishEvent: Event, function):
        Thread.__init__(self)
        self._finishEvent = finishEvent  # type: Event
        self.enableEvent = enableEvent  # type: Event
        self._function = function
        self.start()

    def run(self):
        while not self._finishEvent.wait(TIME_INTERVAL):
            if self.enableEvent.is_set():
                self._function()
