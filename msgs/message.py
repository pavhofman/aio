"""
Abstract message
"""
from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID


class Message():
    def __init__(self, fromID: ModuleID, typeID: MsgID, forID: ModuleID, groupID: GroupID):
        self.typeID = typeID
        self.fromID = fromID
        self.forID = forID
        self.groupID = groupID

    def toString(self) -> str:
        return "typeID: " + str(self.typeID) \
               + "; fromID: " + str(self.fromID) \
               + "; forID: " + str(self.forID) \
                + "; groupID: " + str(self.groupID)