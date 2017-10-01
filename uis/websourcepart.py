import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.audioparamsmsg import AudioParamsMsg, ParamsItem
from msgs.integermsg import IntegerMsg
from msgs.jsonmsg import JsonMsg
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
        label = StatusLabel(self.name)
        label.decorateForStatus(self.sourceStatus)
        return label

    def _createActivationButton(self) -> StatusButton:
        button = StatusButton(text=self.name)
        button.set_on_click_listener(self._onActivateButtonPressed)
        button.decorateForStatus(self.sourceStatus)
        return button

    def setStatus(self, newStatus: SourceStatus) -> bool:
        if super().setStatus(newStatus):
            self._decorateComponentsForNewStatus()
            if self.sourceStatus == SourceStatus.UNAVAILABLE:
                # clearing source boxes
                self._selectorBox.clear()
                self._trackBox.clear()
            else:
                if not self._hasDataFromSource():
                    self._requestInitialDataFromSource()

                if self.sourceStatus == SourceStatus.ACTIVATED:
                    # activation
                    pass
                elif self.sourceStatus == SourceStatus.NOT_ACTIVATED:
                    # not doing anything on this level
                    pass
            return True
        else:
            return False

    def getOverviewLabel(self) -> StatusLabel:
        return self._overviewLabel

    def getTrackBox(self) -> TrackDetailsBox:
        return self._trackBox

    def _decorateComponentsForNewStatus(self) -> None:
        self._overviewLabel.decorateForStatus(self.sourceStatus)
        self._activationButton.decorateForStatus(self.sourceStatus)

    def getSelectorFSBox(self) -> gui.Widget:
        return self._selectorBox

    # noinspection PyUnusedLocal
    def _onActivateButtonPressed(self, widget) -> None:
        if self.sourceStatus.isAvailable() and not self.sourceStatus.isActivated():
            # changing
            self._app.sendSwitchSourceReq(source=self, activate=True)

    def getActivationButton(self) -> StatusButton:
        return self._activationButton

    def _createTrackBox(self) -> 'TrackDetailsBox':
        return TrackDetailsBox(self._app, self, showSkipBtns=False, showNextBtns=False)

    def showSelectorBox(self):
        self._app.setFSBox(self._selectorBox)

    def handleMsgFromSource(self, msg) -> bool:
        if msg.typeID == MsgID.TRACK_INFO:
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
        elif msg.typeID == MsgID.METADATA_INFO:
            msg = msg  # type: JsonMsg
            self._drawMetadata(mdJson=msg.json)
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
            # switching to node selector box automatically
            self.showSelectorBox()
        elif PlaybackStatus.PAUSED == status:
            self._trackBox.drawPlaybackPaused()
            self._selectorBox.trackBox.drawPlaybackPaused()
        elif PlaybackStatus.PLAYING == status:
            self._trackBox.drawPlaybackPlaying()
            self._selectorBox.trackBox.drawPlaybackPlaying()

    def _drawParams(self, paramsItem: ParamsItem):
        self._trackBox.drawParams(paramsItem)

    def _drawMetadata(self, mdJson: str):
        self._trackBox.drawMetadata(mdJson)

    def _requestInitialDataFromSource(self):
        # request root node
        self._selectorBox.sendReqRootNodeMsg()

    def _hasDataFromSource(self) -> bool:
        return self._selectorBox.hasDataFromSource()
