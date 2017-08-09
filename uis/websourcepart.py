import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.nodemsg import NodeMsg
from msgs.trackmsg import TrackItem, TrackMsg
from remi import gui
from sources.playbackstatus import PlaybackStatus
from sources.sourcestatus import SourceStatus
from uis.nodeselectfscontainer import NodeSelectFSContainer
from uis.sourcepart import SourcePart
from uis.statuswidgets import StatusButton, StatusLabel
from uis.trackcontainer import TrackContainer

if TYPE_CHECKING:
    from uis.webapp import WebApp


class WebSourcePart(SourcePart, abc.ABC):
    def __init__(self, sourceID: ModuleID, name: str, app: 'WebApp'):
        SourcePart.__init__(self, sourceID=sourceID)
        self._app = app  # type: 'WebApp'
        self.name = name
        self._initGUIComponents()

    def _initGUIComponents(self) -> None:
        self._overviewLabel = self._createOverviewLabel()
        self._selectorContainer = self._createSelectorContainer()
        self._activationButton = self._createActivationButton()
        self._trackContainer = self._createTrackContainer()

    def _createSelectorContainer(self) -> NodeSelectFSContainer:
        return NodeSelectFSContainer(self._app, self)

    def _createOverviewLabel(self) -> StatusLabel:
        label = StatusLabel(self._getLabelText())
        label.decorateForStatus(self.sourceStatus)
        return label

    def _createActivationButton(self) -> StatusButton:
        button = StatusButton(text=self._getLabelText())
        button.set_on_click_listener(self._onActivateButtonPressed)
        button.decorateForStatus(self.sourceStatus)
        return button

    def setStatus(self, newStatus: SourceStatus) -> None:
        if newStatus != self.sourceStatus:
            super().setStatus(newStatus)
            self._updateComponentsForNewStatus()

    def getOverviewLabel(self) -> StatusLabel:
        return self._overviewLabel

    # noinspection PyUnusedLocal
    def _updateComponentsForNewStatus(self) -> None:
        self._overviewLabel.set_text(self._getLabelText())
        self._overviewLabel.decorateForStatus(self.sourceStatus)
        self._activationButton.set_text(self._getLabelText())
        self._activationButton.decorateForStatus(self.sourceStatus)

    def _getLabelText(self) -> str:
        return self.name + str(self.sourceStatus.value)

    def getSelectorFSContainer(self) -> gui.Widget:
        return self._selectorContainer

    # noinspection PyUnusedLocal
    def _onActivateButtonPressed(self, widget) -> None:
        if self.sourceStatus.isAvailable():
            # changing
            self._app.sendSwitchSourceReq(source=self, activate=not self.sourceStatus.isActivated())
        # closing
        self.showSelectorContainer()

    def getActivationButton(self) -> StatusButton:
        return self._activationButton

    def _createTrackContainer(self) -> 'TrackContainer':
        return TrackContainer(self._app, self)

    def showSelectorContainer(self):
        self._app.setFSContainer(self._selectorContainer)

    def handleMsgFromSource(self, msg) -> bool:
        if msg.typeID == MsgID.SOURCE_STATUS_INFO:
            msg = msg  # type: IntegerMsg
            self._setSourceStatus(statusID=msg.value)
            return True
        elif msg.typeID == MsgID.TRACK_INFO:
            msg = msg  # type: TrackMsg
            self._drawTrack(trackItem=msg.trackItem)
            return True
        elif msg.typeID == MsgID.NODE_INFO:
            msg = msg  # type: NodeMsg
            self._selectorContainer.drawStruct(msg.nodeStruct)
            return True
        elif msg.typeID == MsgID.SOURCE_PLAYBACK_INFO:
            msg = msg  # type: IntegerMsg
            self._showPlaybackStatus(statusID=msg.value)
            return True
        else:
            return False

    def _setSourceStatus(self, statusID: int):
        status = SourceStatus(statusID)
        # update source
        self.setStatus(status)
        # update trackcontainer
        if status.isActivated():
            self._app.mainFSContainer.setTrackContainer(self._trackContainer)

        elif self._app.getActiveSource() is None:
            # deactivated
            self._app.mainFSContainer.setNoTrackContainer()

    def _drawTrack(self, trackItem: TrackItem) -> None:
        self._trackContainer.drawTrack(trackItem)
        self._selectorContainer.drawTrack(trackItem)

    def _showPlaybackStatus(self, statusID: int):
        status = PlaybackStatus(statusID)
        if PlaybackStatus.STOPPED == status:
            self._trackContainer.drawPlaybackStopped()
            self._selectorContainer.drawPlaybackStopped()
        elif PlaybackStatus.PAUSED == status:
            self._trackContainer.drawPlaybackPaused()
            self._selectorContainer.drawPlaybackPaused()
        elif PlaybackStatus.PLAYING == status:
            self._trackContainer.drawPlaybackPlaying()
            self._selectorContainer.drawPlaybackPlaying()
