import abc

from remi import gui

from moduleid import ModuleID
from sourcestatus import SourceStatus
from uis.sourceuipart import SourceUIPart
from uis.statuswidgets import StatusButton, StatusLabel
from uis.webapp import WebApp


class WebSourceUIPart(SourceUIPart, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, name: str):
        SourceUIPart.__init__(self, id=id)
        self._app = None
        self.name = name
        self._overviewLabel = None  # type: StatusLabel
        self._selectorContainer = None
        self._activationButton = None  # type: StatusButton
        self._trackContainer = None

    # delayed initialization after app started
    def appIsRunning(self, app: WebApp) -> None:
        self._app = app
        self._initGUIComponents()

    def _initGUIComponents(self) -> None:
        self._overviewLabel = self._createOverviewLabel()
        self._selectorContainer = gui.Widget(width=self._app.getWidth(), height=self._app.getHeight(),
                                             margin='0px auto',
                                             layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
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
            self._app.switchSource(source=self, activate=not self.status.isActive())
        # closing
        self._app.showPrevFSContainer()

    def getActivationButton(self) -> StatusButton:
        return self._activationButton

    def _createTrackContainer(self) -> gui.Widget:
        container = gui.Widget(width=400)
        container.style['display'] = 'block'
        container.style['overflow'] = 'auto'
        container.style['text-align'] = 'center'
        self._fillTrackContainer(container)
        return container

    def getTrackContainer(self) -> gui.Widget:
        return self._trackContainer

    @abc.abstractmethod
    def _fillTrackContainer(self, container: gui.Widget) -> None:
        pass

    @abc.abstractmethod
    def _fillSelectorContainer(self, container: gui.Widget) -> None:
        pass
