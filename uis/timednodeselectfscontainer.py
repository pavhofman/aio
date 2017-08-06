from typing import TYPE_CHECKING

from msgs.trackmsg import TrackItem
from remi import gui
from uis.nodeselectfscontainer import NodeSelectFSContainer

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TimedNodeSelectFSContainer(NodeSelectFSContainer):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        NodeSelectFSContainer.__init__(self, app, sourcePart)

    def _createTrackContainer(self, width: int, height: int) -> gui.Widget:
        box = super()._createTrackContainer(width, height)
        self._timePosLabel = gui.Label(text="")
        box.append(self._timePosLabel, "2")
        self._trackDuration = gui.Label(text="")
        box.append(self._trackDuration, "3")
        return box

    def drawTrack(self, trackItem: TrackItem) -> None:
        # TODO - check for nodeID?
        super().drawTrack(trackItem)
        duration = str(trackItem.duration) if trackItem.duration is not None else ""
        self._trackDuration.set_text(duration)

    def drawTimePos(self, timePos: int) -> None:
        self._timePosLabel.set_text(str(timePos))
