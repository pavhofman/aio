import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from remi import gui, Button
from sourcestatus import SourceStatus
from uis.sourcepart import SourcePart
from uis.statuswidgets import StatusButton, StatusLabel

if TYPE_CHECKING:
    from uis.webapp import WebApp


class WebSourcePart(SourcePart, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, name: str, app: 'WebApp'):
        SourcePart.__init__(self, id=id)
        self._app = app  # type: 'WebApp'
        self.name = name
        self._initGUIComponents()

    def _initGUIComponents(self) -> None:
        self._overviewLabel = self._createOverviewLabel()
        self._selectorContainer = gui.VBox(width=self._app.getWidth(), height=self._app.getHeight(), margin='0px auto')
        self._fillSelectorContainer(self._selectorContainer)
        self._activationButton = self._createActivationButton()
        self._trackContainer = self._createTrackContainer()

    def _createOverviewLabel(self) -> StatusLabel:
        label = StatusLabel(self._getLabelText())
        label.decorateForStatus(self.status)
        return label

    def _createActivationButton(self) -> StatusButton:
        button = StatusButton(text=self._getLabelText())
        button.set_on_click_listener(self._onActivateButtonPressed)
        button.decorateForStatus(self.status)
        return button

    def setStatus(self, newStatus: SourceStatus) -> None:
        if newStatus != self.status:
            super().setStatus(newStatus)
            self._updateComponentsForNewStatus()

    def getOverviewLabel(self) -> StatusLabel:
        return self._overviewLabel

    # noinspection PyUnusedLocal
    def _updateComponentsForNewStatus(self) -> None:
        self._overviewLabel.set_text(self._getLabelText())
        self._overviewLabel.decorateForStatus(self.status)
        self._activationButton.set_text(self._getLabelText())
        self._activationButton.decorateForStatus(self.status)

    def _getLabelText(self) -> str:
        return self.name + str(self.status.value)

    def getSelectorFSContainer(self) -> gui.Widget:
        return self._selectorContainer

    # noinspection PyUnusedLocal
    def _onActivateButtonPressed(self, widget) -> None:
        if self.status.isAvailable():
            # changing
            self._app.sendSwitchSourceReq(source=self, activate=not self.status.isActive())
        # closing
        self._app.showPrevFSContainer()

    def getActivationButton(self) -> StatusButton:
        return self._activationButton

    def _createTrackContainer(self) -> gui.Widget:
        container = gui.Widget(width=400)
        self._fillTrackContainer(container)
        button = Button(text="Výběr tracku")
        button.set_on_click_listener(self._onOpenSelectorButtonPressed)
        container.append(button)
        return container

    # noinspection PyUnusedLocal
    def _onOpenSelectorButtonPressed(self, widget):
        self._app.setFSContainer(self._selectorContainer)

    def getTrackContainer(self) -> gui.Widget:
        return self._trackContainer

    @abc.abstractmethod
    def _fillTrackContainer(self, container: gui.Widget) -> None:
        pass

    @abc.abstractmethod
    def _fillSelectorContainer(self, container: gui.Widget) -> None:
        pass

    def handleMsgFromSource(self, msg) -> bool:
        if msg.typeID == MsgID.SOURCE_STATUS_INFO:
            msg = msg  # type: IntegerMsg
            self._setSourceStatus(msg.fromID, msg.value)
            return True
        else:
            return False

    def _setSourceStatus(self, sourceID: ModuleID, statusID: int):
        status = SourceStatus(statusID)
        # update source
        self.setStatus(status)
        # update trackcontainer
        if status.isActive():
            self._app.mainFSContainer.setTrackContainer(self.getTrackContainer())

        elif self._app.getActiveSource() is None:
            # deactivated
            self._app.mainFSContainer.setNoTrackContainer()