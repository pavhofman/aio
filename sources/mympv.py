from typing import TYPE_CHECKING

from config import VOLUME_PROPERTY
from sources.mpv import MPV, MPVCommandError

if TYPE_CHECKING:
    from sources.usesmpv import UsesMPV


class MyMPV(MPV):
    # -------------------------------------------------------------------------
    # Initialization.
    # -------------------------------------------------------------------------

    # The mpv process and the communication code run in their own thread
    # context. This results in the callback methods below being run in that
    # thread as well.
    def __init__(self, source: 'UsesMPV'):
        # Pass a window id to embed mpv into that window. Change debug to True
        # to see the json communication.
        super().__init__(window_id=None, debug=False)
        self.source = source

    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------

    # property change events:
    # "time-pos" -> on_property_time_pos().

    def on_property_chapter(self, chapter=None):
        self.source.chapterWasChanged(chapter)

    def on_property_metadata(self, metadata=None):
        self.source.metadataWasChanged(metadata)

    def on_property_pause(self, pause=None):
        self.source.pauseWasChanged(pause)

    def on_property_path(self, filePath: str = None):
        self.source.pathWasChanged(filePath)

    def on_property_idle(self, idle: bool = None):
        self.source.idleWasChanged(idle)


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
