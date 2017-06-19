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
        subContainerLeft = gui.Widget(width=400)
        subContainerLeft.style['display'] = 'block'
        subContainerLeft.style['overflow'] = 'auto'
        subContainerLeft.style['text-align'] = 'center'
        self._currentLeftContainer = subContainerLeft
        self._overviewContainer = OverviewPanel(app)
        self.append(subContainerLeft)
        self.append(self._overviewContainer)

    def setVolume(self, value: int):
        self._overviewContainer.setVolume(value)
