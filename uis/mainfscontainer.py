from typing import TYPE_CHECKING

from remi import gui
from uis.overviewpanel import OverviewPanel

TRACK_CONTAINER_KEY = '1'
OVERVIEW_CONTAINER_KEY = '2'


if TYPE_CHECKING:
    from uis.webapp import WebApp


class MainFSContainer(gui.HBox):
    def __init__(self, app: 'WebApp'):
        super().__init__(width=app.getWidth(), height=app.getHeight(), margin='0px auto',
                         layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        self._app = app
        self._noTrackContainer = self._createNoSourceTrackContainer()
        self.setNoTrackContainer()
        self._overviewContainer = OverviewPanel(app)
        self.append(self._overviewContainer, OVERVIEW_CONTAINER_KEY)

    @staticmethod
    def _createNoSourceTrackContainer() -> gui.Widget:
        container = gui.Widget(width=400)
        container.style['text-align'] = 'center'
        container.append(gui.Label(text="No active source"))
        return container

    def setVolume(self, value: int):
        self._overviewContainer.setVolume(value)

    def setTrackContainer(self, container: gui.Widget) -> None:
        if not self._isCurrentTrackContainer(container):
            self.append(container, TRACK_CONTAINER_KEY)

    def _isCurrentTrackContainer(self, container: gui.Widget):
        return TRACK_CONTAINER_KEY in self.children.keys() and container == self.children[TRACK_CONTAINER_KEY]

    def setNoTrackContainer(self):
        self.setTrackContainer(self._noTrackContainer)
