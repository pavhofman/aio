from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message


class AudioParamsMsg(Message):
    """
    Msg with details of currently played audio format
    """

    def __init__(self, paramsItem: 'ParamsItem', fromID: ModuleID, forID=ModuleID.ANY,
                 groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=MsgID.AUDIOPARAMS_INFO, forID=forID, groupID=groupID)
        self.paramsItem = paramsItem

    def __str__(self) -> str:
        return super().__str__() \
               + "; paramsItem: " + str(self.paramsItem)


class ParamsItem:
    def __init__(self, rate: int, bits: int, channels: int):
        self.rate = rate
        self.bits = bits
        self.channels = channels

    def __str__(self) -> str:
        return super().__str__() \
               + "; rate: " + str(self.rate) \
               + "; bits: " + str(self.bits) \
               + "; channels: " + str(self.channels)
