from typing import TYPE_CHECKING

from msgs.trackmsg import TrackItem
from remi import gui
from uis.addsplaybackbuttons import AddsPlaybackButtons

if TYPE_CHECKING:
    from uis.webapp import WebApp
    from uis.websourcepart import WebSourcePart


class SimpleTrackBox(gui.HBox, AddsPlaybackButtons):
    def __init__(self, width: int, height: int, app: 'WebApp', sourcePart: 'WebSourcePart'):
        gui.HBox.__init__(self, width=width, height=height, margin='0px auto')
        AddsPlaybackButtons.__init__(self, app=app, sourcePart=sourcePart)
        self._sourcePart = sourcePart
        self._app = app
        self._trackLabel = gui.Label(text="")
        self.append(self._trackLabel, "1")

    # noinspection PyUnusedLocal
    def drawTrack(self, trackItem: TrackItem) -> None:
        self._trackLabel.set_text(trackItem.label)
        self.drawPlaybackPlaying()

    def _clearTrackInfo(self):
        self._trackLabel.set_text("")
