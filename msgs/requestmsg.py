from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message


class RequestMsg(Message):
    def __init__(self, fromID: ModuleID, typeID: MsgID, forID: ModuleID=ModuleID.ANY, groupID: GroupID=GroupID.ANY):
        super().__init__(fromID=fromID, forID=forID, typeID=typeID, groupID=groupID)
