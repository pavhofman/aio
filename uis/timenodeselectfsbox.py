from typing import TYPE_CHECKING

from uis.nodeselectfsbox import NodeSelectFSBox
from uis.simpletimetrackbox import SimpleTimeTrackBox

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TimeNodeSelectFSBox(NodeSelectFSBox):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        NodeSelectFSBox.__init__(self, app, sourcePart)

    def _createTrackBox(self, width: int, height: int) -> SimpleTimeTrackBox:
        return SimpleTimeTrackBox(width=width, height=height, sourcePart=self._sourcePart)

    def drawTimePos(self, timePos: int, duration: int):
        self._trackBox.drawTimePos(timePos, duration)
