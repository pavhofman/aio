from typing import TYPE_CHECKING

from msgs.trackmsg import TrackItem
from remi import gui
from sources.playbackstatus import PlaybackStatus
from uis.addsplaybackbuttons import AddsPlaybackButtons

if TYPE_CHECKING:
    from uis.webapp import WebApp
    from uis.websourcepart import WebSourcePart


class SimpleTrackBox(gui.HBox, AddsPlaybackButtons):
    def __init__(self, width: int, height: int, app: 'WebApp', sourcePart: 'WebSourcePart'):
        gui.HBox.__init__(self, width=width, height=height, margin='0px auto')
        # never shows skip buttons - would not fit there
        AddsPlaybackButtons.__init__(self, app=app, posKey="10", sourcePart=sourcePart)
        self._sourcePart = sourcePart
        self._app = app
        self._trackLabel = gui.Label(text="")
        self.append(self._trackLabel, "1")

    # noinspection PyUnusedLocal
    def drawTrack(self, trackItem: TrackItem) -> None:
        self._trackLabel.set_text(trackItem.label)
        self._updateButtonsFor(PlaybackStatus.PLAYING)

    def drawPlaybackPaused(self) -> None:
        self._updateButtonsFor(PlaybackStatus.PAUSED)

    def drawPlaybackPlaying(self) -> None:
        self._updateButtonsFor(PlaybackStatus.PLAYING)

    def drawPlaybackStopped(self) -> None:
        self._updateButtonsFor(PlaybackStatus.STOPPED)
        self._clearTrackInfo()

    def _clearTrackInfo(self):
        self._trackLabel.set_text("")

    def clear(self):
        self._hideButtons()
        self._clearTrackInfo()
