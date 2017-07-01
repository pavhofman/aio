from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message


class IntegerMsg(Message):
    """
    Msg with single int value
    """

    def __init__(self, value: int, fromID: ModuleID, typeID: MsgID, forID=ModuleID.ANY, groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=typeID, forID=forID, groupID=groupID)
        self.value = value

    def __str__(self) -> str:
        return super().__str__() + "; Value: " + str(self.value)


class BiIntegerMsg(Message):
    """
    Msg with two int values
    """

    def __init__(self, value1: int, value2: int, fromID: ModuleID, typeID: MsgID, forID=ModuleID.ANY,
                 groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=typeID, forID=forID, groupID=groupID)
        self.value1 = value1
        self.value2 = value2

    def __str__(self) -> str:
        return super().__str__() + "; Value1: " + str(self.value1) + "; Value2: " + str(self.value2)
