import abc
from typing import TYPE_CHECKING, Optional

from moduleid import ModuleID
from remi import gui, Button
from sourcestatus import SourceStatus
from uis.sourceuipart import SourceUIPart
from uis.statuswidgets import StatusButton, StatusLabel

if TYPE_CHECKING:
    from uis.webapp import WebApp


class WebSourceUIPart(SourceUIPart, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, name: str):
        SourceUIPart.__init__(self, id=id)
        self._app = None  # type: Optional[WebApp]
        self.name = name
        self._overviewLabel = None  # type: StatusLabel
        self._selectorContainer = None
        self._activationButton = None  # type: StatusButton
        self._trackContainer = None

    # delayed initialization after app started
    def appIsRunning(self, app: 'WebApp') -> None:
        self._app = app
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
