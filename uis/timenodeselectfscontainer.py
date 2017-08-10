from typing import TYPE_CHECKING

from uis.nodeselectfscontainer import NodeSelectFSContainer
from uis.simpletimetrackcontrainer import SimpleTimeTrackContainer

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TimeNodeSelectFSContainer(NodeSelectFSContainer):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        NodeSelectFSContainer.__init__(self, app, sourcePart)

    def _createTrackContainer(self, width: int, height: int) -> SimpleTimeTrackContainer:
        return SimpleTimeTrackContainer(width=width, height=height, app=self._app, sourcePart=self._sourcePart)
