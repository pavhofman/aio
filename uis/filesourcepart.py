from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgs.trackmsg import TrackItem
from remi import gui
from uis.treesourcepart import TreeSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class FileSourcePart(TreeSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(sourceID=ModuleID.FILE_SOURCE, name="File", app=app)

    def _fillTrackContainer(self, container: gui.Widget) -> None:
        container.append(gui.Label(text=self.name))

    def _showTrackInTrackContainer(self, trackItem: TrackItem) -> None:
        # TODO - check for nodeID?
        # self._trackContainer.empty()
        # self._trackContainer.append(gui.Label(text=trackItem.label))
        # self._trackContainer.append(gui.Label(text=str(trackItem.duration)))
        pass

    def _showTimeInTrackContainer(self, timePos: int) -> None:
        # TODO - check for nodeID?
        # self._trackContainer.empty()
        # self._trackContainer.append(gui.Label(text=str(timePos)))
        pass
