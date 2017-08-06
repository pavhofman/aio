from typing import TYPE_CHECKING

from moduleid import ModuleID
from remi import gui
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class AnalogSourcePart(WebSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(sourceID=ModuleID.ANALOG_SOURCE, name="Analog", app=app)

    def _fillSelectorContainer(self, container: gui.Widget) -> None:
        pass
