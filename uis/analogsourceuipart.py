from typing import TYPE_CHECKING

from moduleid import ModuleID
from remi import gui
from uis.websourceuipart import WebSourceUIPart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class AnalogSourceUIPart(WebSourceUIPart):
    def __init__(self, app: 'WebApp'):
        super().__init__(id=ModuleID.ANALOG_SOURCE, name="Analog", app=app)

    def _fillTrackContainer(self, container: gui.Widget) -> None:
        container.append(gui.Label(text=self.name))

    def _fillSelectorContainer(self, container: gui.Widget) -> None:
        pass
