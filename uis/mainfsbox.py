from typing import TYPE_CHECKING

from remi import gui
from uis.overviewpanel import OverviewPanel

TRACK_BOX_KEY = '1'
OVERVIEW_BOX_KEY = '2'


if TYPE_CHECKING:
    from uis.webapp import WebApp


class MainFSBox(gui.HBox):
    def __init__(self, app: 'WebApp'):
        super().__init__(width=app.getWidth(), height=app.getHeight(), margin='0px auto',
                         layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        self._app = app
        self._noTrackBox = self._createNoSourceTrackBox()
        self.setNoTrackBox()
        self._overviewBox = OverviewPanel(app)
        self.append(self._overviewBox, OVERVIEW_BOX_KEY)

    @staticmethod
    def _createNoSourceTrackBox() -> gui.Widget:
        box = gui.Widget(width=400)
        box.style['text-align'] = 'center'
        box.append(gui.Label(text="No active source"))
        return box

    def setVolume(self, value: int):
        self._overviewBox.setVolume(value)

    def setTrackBox(self, box: gui.Widget) -> None:
        if not self._isCurrentTrackBox(box):
            self.append(box, TRACK_BOX_KEY)

    def _isCurrentTrackBox(self, box: gui.Widget):
        return TRACK_BOX_KEY in self.children.keys() and box == self.children[TRACK_BOX_KEY]

    def setNoTrackBox(self):
        self.setTrackBox(self._noTrackBox)
