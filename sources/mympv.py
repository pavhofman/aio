from contextlib import contextmanager
from threading import Lock
from typing import TYPE_CHECKING, Optional

from config import VOLUME_PROPERTY
from sources.mpv import MPV, MPVCommandError

if TYPE_CHECKING:
    from sources.usesmpv import UsesMPV

mpvLock = Lock()


@contextmanager
def locked(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


class MyMPV(MPV):
    # -------------------------------------------------------------------------
    # Initialization.
    # -------------------------------------------------------------------------

    # The mpv process and the communication code run in their own thread
    # context. This results in the callback methods below being run in that
    # thread as well.
    def __init__(self, owner: 'UsesMPV'):
        # Pass a window id to embed mpv into that window. Change debug to True
        # to see the json communication.
        self._owner = owner
        super().__init__(window_id=None, debug=False)

    def getOwner(self) -> Optional['UsesMPV']:
        return self._owner

    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------

    # property change events:
    # "time-pos" -> on_property_time_pos().

    def on_property_chapter(self, chapter=None):
        self._owner.chapterWasChanged(chapter)

    def on_property_metadata(self, metadata=None):
        self._owner.metadataWasChanged(metadata)

    def on_property_pause(self, pause=None):
        self._owner.pauseWasChanged(pause)

    def on_property_path(self, filePath: str = None):
        self._owner.pathWasChanged(filePath)

    def on_property_idle(self, idle: bool = None):
        self._owner.idleWasChanged(idle)

    def on_property_audio_params(self, params=None):
        if params:
            self._owner._audioParamsWereChanged(params)

    # -------------------------------------------------------------------------
    # Commands
    # -------------------------------------------------------------------------
    # Many commands must be implemented by changing properties.
    def play(self):
        self.set_property("pause", False)

    def pause(self):
        self.set_property("pause", True)

    def stop(self):
        self.command("stop")

    def setVolume(self, volume: int):
        try:
            self.set_property(VOLUME_PROPERTY, int(volume))
        except MPVCommandError:
            # not running, no problem
            pass

    def command(self, *args):
        """
        Locking to make sure calling command is not interleaved by another thread
        """
        global mpvLock
        with locked(mpvLock):
            return super().command(*args)
