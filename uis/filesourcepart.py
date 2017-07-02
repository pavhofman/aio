from typing import TYPE_CHECKING

from moduleid import ModuleID
from remi import gui
from uis.nodesourcepart import NodeSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class FileSourcePart(NodeSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(id=ModuleID.FILE_SOURCE, name="File", app=app)

    def _fillTrackContainer(self, container: gui.Widget) -> None:
        container.append(gui.Label(text=self.name))
