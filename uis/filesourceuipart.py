from remi import gui

from moduleid import ModuleID
from uis.websourceuipart import WebSourceUIPart


class FileSourceUIPart(WebSourceUIPart):
    def __init__(self):
        super().__init__(id=ModuleID.FILE_SOURCE, name="F")

    def _fillSelectorCont(self, container: gui.Widget):
        pass
