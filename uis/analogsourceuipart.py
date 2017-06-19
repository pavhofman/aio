from remi import gui

from moduleid import ModuleID
from uis.websourceuipart import WebSourceUIPart


class AnalogSourceUIPart(WebSourceUIPart):
    def __init__(self):
        super().__init__(id=ModuleID.ANALOG_SOURCE, name="A")

    def _fillSelectorCont(self, container: gui.Widget):
        pass
