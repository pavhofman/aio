from typing import TYPE_CHECKING

from msgs.trackmsg import TrackItem
from remi import gui, Button
from sources.playbackstatus import PlaybackStatus

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TrackContainer(gui.VBox):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        gui.VBox.__init__(self, width=400, height=app.getHeight(), margin='0px auto')
        self._sourcePart = sourcePart
        self._app = app
        button = Button(text="Select track")
        button.set_on_click_listener(self._onOpenSelectorButtonPressed)
        self.append(button)

    # noinspection PyUnusedLocal
    def _onOpenSelectorButtonPressed(self, widget):
        self._sourcePart.showSelectorContainer()

    def drawTrack(self, trackItem: TrackItem) -> None:
        pass

    def drawPlayback(self, status: PlaybackStatus) -> None:
        pass
