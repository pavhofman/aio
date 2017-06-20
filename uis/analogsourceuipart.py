from remi import gui

from moduleid import ModuleID
from uis.websourceuipart import WebSourceUIPart


class AnalogSourceUIPart(WebSourceUIPart):
    def __init__(self):
        super().__init__(id=ModuleID.ANALOG_SOURCE, name="Analog")

    def _fillTrackContainer(self, container: gui.Widget) -> None:
        container.append(gui.Label(text=self.name))

    def _fillSelectorContainer(self, container: gui.Widget) -> None:
        pass
