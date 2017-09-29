from typing import TYPE_CHECKING

from msgs.audioparamsmsg import ParamsItem
from msgs.trackmsg import TrackItem
from remi import gui, Button
from uis.addsplaybackbuttons import AddsPlaybackButtons
from uis.showsaudioparams import ShowsAudioParams
from uis.showsmetadata import ShowsMetadata
from uis.utils import createBtn

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TrackDetailsBox(gui.VBox, AddsPlaybackButtons, ShowsAudioParams, ShowsMetadata):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        gui.VBox.__init__(self, width=400, height=app.getHeight(), margin='0px auto')
        AddsPlaybackButtons.__init__(self, app=app, sourcePart=sourcePart)
        ShowsAudioParams.__init__(self)
        ShowsMetadata.__init__(self)
        self._sourcePart = sourcePart
        self._app = app
        self._trackLabel = gui.Label(text="")
        self.append(self._trackLabel, "1")

        button = Button(text="Select track")
        button.set_on_click_listener(self._onOpenSelectorButtonPressed)
        self.append(createBtn("Select track", True, self._onOpenSelectorButtonPressed), "20")

    # noinspection PyUnusedLocal
    def _onOpenSelectorButtonPressed(self, widget):
        self._sourcePart.showSelectorBox()

    def drawTrack(self, trackItem: TrackItem) -> None:
        self._trackLabel.set_text(trackItem.label)
        self.drawPlaybackPlaying()

    def drawPlaybackPaused(self) -> None:
        self._updateButtonsPaused()

    def drawPlaybackPlaying(self) -> None:
        self._updateButtonsPlaying()

    def drawPlaybackStopped(self) -> None:
        self._updateButtonsStopped()
        self._clearTrackInfo()

    def _clearTrackInfo(self) -> None:
        self._trackLabel.set_text("")
        self._clearParams()
        self._clearMetadata()

    def drawParams(self, paramsItem: ParamsItem) -> None:
        self._showParams(paramsItem)

    def drawMetadata(self, mdJson: str) -> None:
        self._showMetadata(mdJson)

    def clear(self) -> None:
        # TODO
        self.drawPlaybackStopped()
