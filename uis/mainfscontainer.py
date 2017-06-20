from typing import TYPE_CHECKING

from remi import gui

from uis.overviewpanel import OverviewPanel

if TYPE_CHECKING:
    from uis.webapp import WebApp


class MainFSContainer(gui.Widget):
    def __init__(self, app: 'WebApp'):
        super().__init__(width=app.getWidth(), height=app.getHeight(), margin='0px auto',
                         layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        self._app = app
        self.style['display'] = 'block'
        self.style['overflow'] = 'hidden'
        self._noTrackContainer = self._createNoSourceTrackContainer()
        self._trackContainer = self._noTrackContainer
        self.append(self._trackContainer)
        self._overviewContainer = OverviewPanel(app)
        self.append(self._overviewContainer)

    @staticmethod
    def _createNoSourceTrackContainer() -> gui.Widget:
        container = gui.Widget(width=400)
        container.style['display'] = 'block'
        container.style['overflow'] = 'auto'
        container.style['text-align'] = 'center'
        container.append(gui.Label(text="No active source"))
        return container

    def setVolume(self, value: int):
        self._overviewContainer.setVolume(value)

    def setTrackContainer(self, container: gui.Widget) -> None:
        if container is not self._trackContainer:
            self.empty()
            self._trackContainer = container
            self.append(self._trackContainer)
            self.append(self._overviewContainer)

    def setNoTrackContainer(self):
        self.setTrackContainer(self._noTrackContainer)
