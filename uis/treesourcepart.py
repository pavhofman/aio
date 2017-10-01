import abc
from typing import TYPE_CHECKING, Optional

from dispatcher import Dispatcher
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg, IntegerMsg
from msgs.nodemsg import NodeMsg, NodeStruct, NodeID
from msgs.trackmsg import TrackMsg, TrackItem
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
        # last played trackitem
        self._playedTrackItem = None  # type: Optional[TrackItem]

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
        self._playedTrackItem = trackItem
        pass

    def sendReqNodeMsg(self, nodeID: NodeID, fromIndex: int) -> None:
        msg = BiIntegerMsg(value1=nodeID, value2=fromIndex, fromID=self.id,
                           typeID=MsgID.REQ_NODE,
                           forID=self.sourceID)
        self.dispatcher.distribute(msg)

    def sendPlayNodeMsg(self, nodeID: NodeID) -> None:
        msg = IntegerMsg(value=nodeID, fromID=self.id,
                         typeID=MsgID.PLAY_NODE,
                         forID=self.sourceID)
        self.dispatcher.distribute(msg)

    def sendReqParentNodeMsg(self, nodeID: NodeID) -> None:
        msg = IntegerMsg(value=nodeID, fromID=self.id,
                         typeID=MsgID.REQ_PARENT_NODE,
                         forID=self.sourceID)
        self.dispatcher.distribute(msg)

    def _statusChangedToUnavailable(self) -> None:
        super()._statusChangedToUnavailable()
        self._playedTrackItem = None