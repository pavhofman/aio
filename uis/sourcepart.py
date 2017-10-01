import logging

from cansendmessage import CanSendMessage
from dispatcher import Dispatcher
from moduleid import ModuleID
from msgid import MsgID
from msgs.audioparamsmsg import AudioParamsMsg, ParamsItem
from msgs.integermsg import IntegerMsg, BiIntegerMsg
from msgs.jsonmsg import JsonMsg
from sources.playbackstatus import PlaybackStatus
from sources.sourcestatus import SourceStatus

"""
Source part supporting general sources. Does not handle any tree-related messages
"""


class SourcePart(CanSendMessage):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: Dispatcher, sourceID: ModuleID):
        CanSendMessage.__init__(self, id=id, dispatcher=dispatcher)
        self.sourceID = sourceID
        self.sourceStatus = SourceStatus.UNAVAILABLE

    def handleMsgFromSource(self, msg) -> bool:
        if msg.typeID == MsgID.SOURCE_PLAYBACK_INFO:
            msg = msg  # type: IntegerMsg
            statusID = msg.value
            status = PlaybackStatus(statusID)
            self._handlePlaybackStatus(status=status)
            return True
        elif msg.typeID == MsgID.AUDIOPARAMS_INFO:
            msg = msg  # type: AudioParamsMsg
            self._handleAudioParams(msg.paramsItem)
            return True
        elif msg.typeID == MsgID.METADATA_INFO:
            msg = msg  # type: JsonMsg
            self._handleMetadata(msg.json)
            return True
        elif msg.typeID == MsgID.TIME_POS_INFO:
            msg = msg  # type: BiIntegerMsg
            self._handleTimePos(timePos=msg.value1, duration=msg.value2)
        else:
            return False

    def _handlePlaybackStatus(self, status: PlaybackStatus) -> None:
        pass

    def _handleAudioParams(self, paramsItem: ParamsItem) -> None:
        pass

    def _handleMetadata(self, json: str):
        pass

    def _handleTimePos(self, timePos: int, duration: int) -> None:
        pass

    def setStatus(self, newStatus: SourceStatus) -> bool:
        if newStatus != self.sourceStatus:
            oldStatus = self.sourceStatus
            self.sourceStatus = newStatus
            self._statusChanged()
            logging.debug(str(self) + ": changed status from " + str(oldStatus))
            if self.sourceStatus == SourceStatus.UNAVAILABLE:
                self._statusChangedToUnavailable()
            else:
                # is available
                self._statusChangedToAvailable()
                if self.sourceStatus == SourceStatus.ACTIVATED:
                    # activation
                    self._statusChangedToActivated()
                elif self.sourceStatus == SourceStatus.NOT_ACTIVATED:
                    # not doing anything on this level
                    self._statusChangedToNotActivated()
            return True
        else:
            return False

    def _statusChanged(self) -> None:
        pass

    def _statusChangedToAvailable(self) -> None:
        if not self._hasDataFromSource():
            self._requestInitialDataFromSource()

    def _statusChangedToNotActivated(self) -> None:
        pass

    def _statusChangedToActivated(self) -> None:
        pass

    def _statusChangedToUnavailable(self) -> None:
        pass

    def __str__(self) -> str:
        return super().__str__() \
               + "; sourceID: " + str(self.sourceID) \
               + "; sourceStatus: " + str(self.sourceStatus)

    def _hasDataFromSource(self) -> bool:
        return True

    def _requestInitialDataFromSource(self) -> None:
        pass
