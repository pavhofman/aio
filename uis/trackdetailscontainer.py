from typing import TYPE_CHECKING

from msgs.trackmsg import TrackItem
from remi import gui, Button
from uis.addsplaybackbuttons import AddsPlaybackButtons
from uis.utils import createBtn

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TrackDetailsContainer(gui.VBox, AddsPlaybackButtons):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        gui.VBox.__init__(self, width=400, height=app.getHeight(), margin='0px auto')
        AddsPlaybackButtons.__init__(self, app=app, sourcePart=sourcePart)
        self._sourcePart = sourcePart
        self._app = app
        self._trackLabel = gui.Label(text="")
        self.append(self._trackLabel, "1")

        button = Button(text="Select track")
        button.set_on_click_listener(self._onOpenSelectorButtonPressed)
        self.append(createBtn("Select track", True, self._onOpenSelectorButtonPressed), "20")

    def _onOpenSelectorButtonPressed(self, widget):
        self._sourcePart.showSelectorContainer()

    # noinspection PyUnusedLocal
    def drawTrack(self, trackItem: TrackItem) -> None:
        self._trackLabel.set_text(trackItem.label)
        self.drawPlaybackPlaying()

    def _clearTrackInfo(self):
        self._trackLabel.set_text("")
