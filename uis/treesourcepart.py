import abc
from typing import TYPE_CHECKING, Optional

from dispatcher import Dispatcher
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg, IntegerMsg
from msgs.nodemsg import NodeMsg, NodeStruct, NodeID
from msgs.trackmsg import TrackMsg, TrackItem
from sources.playbackstatus import PlaybackStatus
from uis.sourcepart import SourcePart

if TYPE_CHECKING:
    pass

"""
Source part supporting treesources
"""


class TreeSourcePart(SourcePart, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: Dispatcher, sourceID: ModuleID, name: str):
        SourcePart.__init__(self, id=id, dispatcher=dispatcher, sourceID=sourceID)
        self.name = name
        # currently played trackitem
        self._playingTrackItem = None  # type: Optional[TrackItem]

    def handleMsgFromSource(self, msg) -> bool:
        if super().handleMsgFromSource(msg):
            return True
        if msg.typeID == MsgID.TRACK_INFO:
            msg = msg  # type: TrackMsg
            self._handleTrackItem(msg.trackItem)
            return True
        elif msg.typeID == MsgID.NODE_INFO:
            msg = msg  # type: NodeMsg
            self._handleNodeInfo(msg.nodeStruct)
            return True
        else:
            return False

    def _handleNodeInfo(self, nodeStruct: NodeStruct) -> None:
        pass

    def _handleTrackItem(self, trackItem: TrackItem) -> None:
        self._playingTrackItem = trackItem
        pass

    def _handlePlaybackStatus(self, status: PlaybackStatus) -> None:
        super()._handlePlaybackStatus(status)
        # clearing the playedTrackItem
        if status == PlaybackStatus.STOPPED:
            self._playingTrackItem = None

    def sendReqNodeMsg(self, nodeID: NodeID, fromIndex: int) -> None:
        msg = BiIntegerMsg(value1=nodeID, value2=fromIndex, fromID=self.id,
                           typeID=MsgID.REQ_NODE,
                           forID=self.sourceID)
        self.dispatcher.distribute(msg)

    def sendPlayNodeMsg(self, nodeID: NodeID) -> None:
        self.__sendIntegerNodeMsgToSource(MsgID.PLAY_NODE, nodeID)

    def sendReqParentNodeMsg(self, nodeID: NodeID) -> None:
        self.__sendIntegerNodeMsgToSource(MsgID.REQ_PARENT_NODE, nodeID)

    def sendCreateBookmarkMsg(self, nodeID: NodeID) -> None:
        self.__sendIntegerNodeMsgToSource(MsgID.CREATE_NODE_BOOKMARK, nodeID)

    def sendDeleteBookmarkMsg(self, nodeID: NodeID) -> None:
        self.__sendIntegerNodeMsgToSource(MsgID.DELETE_NODE_BOOKMARK, nodeID)

    def __sendIntegerNodeMsgToSource(self, msgID: MsgID, nodeID: NodeID):
        msg = IntegerMsg(value=nodeID, fromID=self.id,
                         typeID=msgID,
                         forID=self.sourceID)
        self.dispatcher.distribute(msg)
