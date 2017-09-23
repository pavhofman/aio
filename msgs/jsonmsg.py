from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message


class JsonMsg(Message):
    """
    Msg with json string
    """

    def __init__(self, json: str, fromID: ModuleID, typeID: MsgID, forID=ModuleID.ANY,
                 groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=typeID, forID=forID, groupID=groupID)
        self.json = json

    def __str__(self) -> str:
        return super().__str__() \
               + "; JSON: " + self.json
