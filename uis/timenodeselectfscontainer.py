from typing import TYPE_CHECKING

from remi import gui
from uis.nodeselectfscontainer import NodeSelectFSContainer

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TimeNodeSelectFSContainer(NodeSelectFSContainer):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        NodeSelectFSContainer.__init__(self, app, sourcePart)

    def _createTrackContainer(self, width: int, height: int) -> gui.Widget:
        box = super()._createTrackContainer(width, height)
        self._timePosLabel = gui.Label(text="")
        box.append(self._timePosLabel, "2")
        self._trackDuration = gui.Label(text="")
        box.append(self._trackDuration, "3")
        return box

    def drawTimePos(self, timePos: int, duration: int) -> None:
        self._timePosLabel.set_text(str(timePos))
        self._trackDuration.set_text(str(duration))

    def drawPlaybackStopped(self):
        super().drawPlaybackStopped()
        self._timePosLabel.set_text("")
        self._trackDuration.set_text("")
