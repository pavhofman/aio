from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgs.trackmsg import TrackItem
from remi import gui
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class AnalogSourcePart(WebSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(sourceID=ModuleID.ANALOG_SOURCE, name="Analog", app=app)

    def _fillTrackContainer(self, container: gui.Widget) -> None:
        container.append(gui.Label(text=self.name))

    def _fillSelectorContainer(self, container: gui.Widget) -> None:
        pass

    def _showTrackInSelectorContainer(self, trackItem: TrackItem) -> None:
        pass

    def _showTimeInSelectorContainer(self, timePos: int) -> None:
        pass

    def _showTrackInTrackContainer(self, trackItem: TrackItem) -> None:
        pass

    def _showTimeInTrackContainer(self, timePos: int) -> None:
        pass
