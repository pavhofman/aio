from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message
from msgs.nodemsg import NodeID


class TrackMsg(Message):
    """
    Msg with details of currently played track
    """

    def __init__(self, trackItem: 'TrackItem', fromID: ModuleID, forID=ModuleID.ANY,
                 groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=MsgID.TRACK_INFO, forID=forID, groupID=groupID)
        self.trackItem = trackItem

    def __str__(self) -> str:
        return super().__str__() \
               + "; trackItem: " + str(self.trackItem)


class TrackItem:
    def __init__(self, nodeID: NodeID, label: str, descr: str):
        self.nodeID = nodeID
        self.label = label
        self.descr = descr

    def __str__(self) -> str:
        return super().__str__() \
               + "; nodeID: " + str(self.nodeID) \
               + "; label: " + self.label \
               + "; descr: " + str(self.descr)
