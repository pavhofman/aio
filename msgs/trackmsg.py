from typing import NewType

from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message

NodeID = NewType('NodeID', int)
NON_EXISTING_NODE_ID = 0


class TrackMsg(Message):
    """
    Msg with details of currently played track
    """

    def __init__(self, nodeID: NodeID, label: str, descr: str, fromID: ModuleID, forID=ModuleID.ANY,
                 groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=MsgID.TRACK_INFO, forID=forID, groupID=groupID)
        self.nodeID = nodeID
        self.label = label
        self.descr = descr

    def __str__(self) -> str:
        return super().__str__() \
               + "; nodeID: " + str(self.nodeID) \
               + "; label: " + self.label \
               + "; descr: " + str(self.descr)
