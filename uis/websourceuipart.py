import abc

from remi import gui

from moduleid import ModuleID
from sourcestatus import SourceStatus
from uis.sourceuipart import SourceUIPart
from uis.webapp import WebApp


class WebSourceUIPart(SourceUIPart, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, name: str):
        super().__init__(id=id)
        self._app = None
        self.name = name
        self._overviewLabel = None
        self._selectorCont = None

    # delayed initialization after app started
    def appRunning(self, app: WebApp):
        self._app = app
        self._initGUIComponents()

    def _initGUIComponents(self):
        self._overviewLabel = gui.Label(self._getLabelText())
        self._selectorCont = gui.Widget(width=self._app.getWidth(), height=self._app.getHeight(), margin='0px auto',
                                        layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        self._fillSelectorCont(self._selectorCont)

    def setStatus(self, newStatus: SourceStatus):
        super().setStatus(newStatus)
        self._updateLabel(newStatus)

    def getOverviewLabel(self):
        return self._overviewLabel

    # noinspection PyUnusedLocal
    def _updateLabel(self, newStatus):
        self._overviewLabel.set_text(self._getLabelText())

    def _getLabelText(self) -> str:
        return self.name + str(self.status.value)

    def getSelectorFSContainer(self):
        return self._selectorCont

    @abc.abstractmethod
    def _fillSelectorCont(self, container: gui.Widget):
        pass
