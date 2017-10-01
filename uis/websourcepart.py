import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgs.audioparamsmsg import ParamsItem
from msgs.nodemsg import NodeStruct
from msgs.trackmsg import TrackItem
from remi import gui
from sources.playbackstatus import PlaybackStatus
from uis.nodeselectfsbox import NodeSelectFSBox
from uis.statuswidgets import StatusButton, StatusLabel
from uis.trackdetailsbox import TrackDetailsBox
from uis.treesourcepart import TreeSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class WebSourcePart(TreeSourcePart, abc.ABC):
    def __init__(self, sourceID: ModuleID, name: str, app: 'WebApp'):
        TreeSourcePart.__init__(self, id=app.id, dispatcher=app.dispatcher,
                                sourceID=sourceID, name=name)
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

    def _statusChanged(self) -> None:
        super()._statusChanged()
        self._decorateComponentsForNewStatus()

    def _statusChangedToUnavailable(self) -> None:
        super()._statusChangedToUnavailable()
        # clearing source boxes
        self._selectorBox.clear()
        self._trackBox.clear()

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

    def showSelectorBox(self) -> None:
        self._app.setFSBox(self._selectorBox)

    def _handleNodeInfo(self, nodeStruct: NodeStruct) -> None:
        super()._handleNodeInfo(nodeStruct)
        self._selectorBox.drawStruct(nodeStruct)

    def _handleTrackItem(self, trackItem: TrackItem) -> None:
        super()._handleTrackItem(trackItem)
        self._drawTrack(trackItem=trackItem)

    def _handleAudioParams(self, paramsItem: ParamsItem) -> None:
        super()._handleAudioParams(paramsItem)
        self._drawParams(paramsItem=paramsItem)

    def _handleMetadata(self, json: str):
        super()._handleMetadata(json)
        self._drawMetadata(mdJson=json)

    def _handlePlaybackStatus(self, status: PlaybackStatus) -> None:
        super()._handlePlaybackStatus(status)
        if PlaybackStatus.STOPPED == status:
            self._trackBox.drawPlaybackStopped()
            self._selectorBox.drawPlaybackStopped()
            # switching to node selector box automatically
            self.showSelectorBox()
        elif PlaybackStatus.PAUSED == status:
            self._trackBox.drawPlaybackPaused()
            self._selectorBox.drawPlaybackPaused()
        elif PlaybackStatus.PLAYING == status:
            self._trackBox.drawPlaybackPlaying()
            self._selectorBox.drawPlaybackPlaying()

    def _drawTrack(self, trackItem: TrackItem) -> None:
        self._trackBox.drawTrack(trackItem)
        self._selectorBox.drawTrack(trackItem)

    def _drawParams(self, paramsItem: ParamsItem) -> None:
        self._trackBox.drawParams(paramsItem)

    def _drawMetadata(self, mdJson: str) -> None:
        self._trackBox.drawMetadata(mdJson)

    def _requestInitialDataFromSource(self) -> None:
        # request root node
        self._selectorBox.sendReqRootNodeMsg()

    def _hasDataFromSource(self) -> bool:
        return self._selectorBox.hasDataFromSource()
