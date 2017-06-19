from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message


class IntegerMsg(Message):
    def __init__(self, value: int, fromID: ModuleID, typeID:MsgID, forID=ModuleID.ANY, groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=typeID, forID=forID, groupID=groupID)
        self.value = value

    def toString(self) -> str:
        return super().toString() + "; Value: " + str(self.value)



