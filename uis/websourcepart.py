import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.audioparamsmsg import AudioParamsMsg, ParamsItem
from msgs.integermsg import IntegerMsg
from msgs.nodemsg import NodeMsg
from msgs.trackmsg import TrackItem, TrackMsg
from remi import gui
from sources.playbackstatus import PlaybackStatus
from sources.sourcestatus import SourceStatus
from uis.nodeselectfsbox import NodeSelectFSBox
from uis.sourcepart import SourcePart
from uis.statuswidgets import StatusButton, StatusLabel
from uis.trackdetailsbox import TrackDetailsBox

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
        self._selectorBox = self._createSelectorBox()
        self._activationButton = self._createActivationButton()
        self._trackBox = self._createTrackBox()

    def _createSelectorBox(self) -> NodeSelectFSBox:
        return NodeSelectFSBox(self._app, self)

    def _createOverviewLabel(self) -> StatusLabel:
        label = StatusLabel(self._getLabelText())
        label.decorateForStatus(self.sourceStatus)
        return label

    def _createActivationButton(self) -> StatusButton:
        button = StatusButton(text=self._getLabelText())
        button.set_on_click_listener(self._onActivateButtonPressed)
        button.decorateForStatus(self.sourceStatus)
        return button

    def setStatus(self, newStatus: SourceStatus) -> bool:
        if super().setStatus(newStatus):
            self._updateComponentsForNewStatus()
            # update trackbox
            if self.sourceStatus.isActivated():
                self._app.mainFSBox.setTrackBox(self._trackBox)

            elif self._app.getActiveSource() is None:
                # deactivated
                self._app.mainFSBox.setNoTrackBox()
            return True
        else:
            return False

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

    def getSelectorFSBox(self) -> gui.Widget:
        return self._selectorBox

    # noinspection PyUnusedLocal
    def _onActivateButtonPressed(self, widget) -> None:
        if self.sourceStatus.isAvailable() and not self.sourceStatus.isActivated():
            # changing
            self._app.sendSwitchSourceReq(source=self, activate=True)
        # closing
        self.showSelectorBox()

    def getActivationButton(self) -> StatusButton:
        return self._activationButton

    def _createTrackBox(self) -> 'TrackDetailsBox':
        return TrackDetailsBox(self._app, self)

    def showSelectorBox(self):
        self._app.setFSBox(self._selectorBox)

    def handleMsgFromSource(self, msg) -> bool:
        if msg.typeID == MsgID.SOURCE_STATUS_INFO:
            msg = msg  # type: IntegerMsg
            status = SourceStatus(msg.value)
            self.setStatus(status)
            return True
        elif msg.typeID == MsgID.TRACK_INFO:
            msg = msg  # type: TrackMsg
            self._drawTrack(trackItem=msg.trackItem)
            return True
        elif msg.typeID == MsgID.NODE_INFO:
            msg = msg  # type: NodeMsg
            self._selectorBox.drawStruct(msg.nodeStruct)
            return True
        elif msg.typeID == MsgID.SOURCE_PLAYBACK_INFO:
            msg = msg  # type: IntegerMsg
            self._showPlaybackStatus(statusID=msg.value)
            return True
        elif msg.typeID == MsgID.AUDIOPARAMS_INFO:
            msg = msg  # type: AudioParamsMsg
            self._drawParams(paramsItem=msg.paramsItem)
            return True
        else:
            return False

    def _drawTrack(self, trackItem: TrackItem) -> None:
        self._trackBox.drawTrack(trackItem)
        self._selectorBox.trackBox.drawTrack(trackItem)

    def _showPlaybackStatus(self, statusID: int):
        status = PlaybackStatus(statusID)
        if PlaybackStatus.STOPPED == status:
            self._trackBox.drawPlaybackStopped()
            self._selectorBox.trackBox.drawPlaybackStopped()
        elif PlaybackStatus.PAUSED == status:
            self._trackBox.drawPlaybackPaused()
            self._selectorBox.trackBox.drawPlaybackPaused()
        elif PlaybackStatus.PLAYING == status:
            self._trackBox.drawPlaybackPlaying()
            self._selectorBox.trackBox.drawPlaybackPlaying()

    def _drawParams(self, paramsItem: ParamsItem):
        self._trackBox.drawParams(paramsItem)
