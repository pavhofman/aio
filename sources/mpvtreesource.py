import abc
import re
from time import sleep
from typing import TYPE_CHECKING, Optional, List, Dict, Generic

from groupid import GroupID
from metadata import Metadata
from moduleid import ModuleID
from msgid import MsgID
from msgs.audioparamsmsg import ParamsItem, AudioParamsMsg
from msgs.integermsg import BiIntegerMsg
from msgs.jsonmsg import JsonMsg
from msgs.nodemsg import NON_EXISTING_NODE_ID
from msgs.trackmsg import TrackMsg, TrackItem
from sources.metadataparser import MetadataParser
from sources.playbackstatus import PlaybackStatus
from sources.treesource import TreeSource, PATH
from sources.usesmpv import UsesMPV

if TYPE_CHECKING:
    from dispatcher import Dispatcher


class MPVTreeSource(TreeSource, UsesMPV, Generic[PATH]):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher', monitorTime: bool):
        self._metadataParser = MetadataParser(rules=self._getMetadataParserRules())
        TreeSource.__init__(self, id=id, dispatcher=dispatcher)
        UsesMPV.__init__(self, monitorTime=monitorTime)

    def _changePlaybackTo(self, playback: PlaybackStatus):
        UsesMPV._changePlaybackTo(self, playback)
        pass

    def _determinePlayback(self) -> PlaybackStatus:
        return UsesMPV._determinePlayback(self)

    def _tryToActivate(self) -> bool:
        # no track selected, stopped
        UsesMPV.reInit(self)
        return True

    def _deactive(self):
        UsesMPV.close(self)
        TreeSource._deactive(self)

    def _makeUnavailable(self):
        UsesMPV.close(self)
        TreeSource._makeUnavailable(self)

    def close(self):
        TreeSource.close(self)
        UsesMPV.close(self)

    def chapterWasChanged(self, chapter: int):
        pass

    def metadataWasChanged(self, metadata: dict):
        if metadata:
            json = self._metadataParser.parseToJsonStr(metadata)
            if json:
                self.__sendMetadataJson(json)

    def __sendMetadataJson(self, mdJson: str) -> None:
        msg = JsonMsg(json=mdJson, fromID=self.id, typeID=MsgID.METADATA_INFO, groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    def _switchedToNewPath(self, path: PATH):
        UsesMPV._resetTimePosTimer(self)
        self._playedNodeID = self._getID(path)
        # waiting for duration being available by mpv
        # ugly hack
        sleep(0.05)
        # send msg
        trackItem = TrackItem(nodeID=self._playedNodeID, label=self._getTrackLabelFor(path), descr="")
        msg = TrackMsg(trackItem=trackItem, fromID=self.id, groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    def _audioParamsWereChanged(self, params: dict):
        bits = self.__parseBits(params)
        if bits:
            item = ParamsItem(params['samplerate'], bits, params['channel-count'])
            msg = AudioParamsMsg(paramsItem=item, fromID=self.id, groupID=GroupID.UI)
            self.dispatcher.distribute(msg)

    @staticmethod
    def __parseBits(params: dict) -> Optional[int]:
        sampleFormat = params['format']  # type: str
        if sampleFormat:
            # typically 's16p', extracting int
            m = re.search('\d+', sampleFormat)
            if m:
                return int(m.group())
        return None

    def pauseWasChanged(self, pause: bool):
        UsesMPV.pauseWasChanged(self, pause)
        self._sendPlaybackInfo(PlaybackStatus.PAUSED if pause else PlaybackStatus.PLAYING)
        pass

    def timePosWasChanged(self, timePosFromStart: int):
        if timePosFromStart is not None and self._playedNodeID != NON_EXISTING_NODE_ID:
            duration = self._getDuration()
            timePos = self._convertTimePos(timePosFromStart)
            if duration is not None and timePos is not None:
                msg = BiIntegerMsg(value1=timePos, value2=duration, fromID=self.id, typeID=MsgID.TIME_POS_INFO,
                                   groupID=GroupID.UI)
                self.dispatcher.distribute(msg)

    def pathWasChanged(self, mpvPath: Optional[str]):
        if mpvPath is None:
            self._sendPlaybackInfo(PlaybackStatus.STOPPED)
        else:
            path = self._getPathFor(mpvPath)
            if path is not None and self._isPlayable(path):
                self._switchedToNewPath(path)

    def _convertTimePos(self, timePosFromStart: int) -> Optional[int]:
        """
        Ancestors can modify the time position (e.g. calculate for chapter)
        Default - no change
        :return:
        """
        return timePosFromStart

    @abc.abstractmethod
    def _getMetadataParserRules(self) -> Dict[Metadata, List[str]]:
        pass
