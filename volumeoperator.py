from typing import TYPE_CHECKING

from groupid import GroupID
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message

if TYPE_CHECKING:
    from dispatcher import Dispatcher

INITIAL_VOLUME = 10

'''
Handles physical volume control
'''


class VolumeOperator(MsgConsumer):
    def __init__(self, dispatcher: 'Dispatcher'):
        # call the thread class
        super().__init__(id=ModuleID.VOLUME_OPERATOR, dispatcher=dispatcher)

    def _initializeInThread(self):
        super()._initializeInThread()
        self.volume = self.__readCurrentVolume()

    def _consume(self, msg: 'Message'):
        if msg.typeID == MsgID.SET_VOL:
            msg = msg  # type: IntegerMsg
            self.__handleSetVolumeMsg(msg)
        elif msg.typeID == MsgID.REQ_CURRENT_VOL_INFO:
            self.__sendCurrentVolume()

    def __handleSetVolumeMsg(self, msg: IntegerMsg):
        newVolume = msg.value
        if newVolume != self.volume:
            self.__setVolume(newVolume)
            self.volume = newVolume
            self.__sendCurrentVolume()

    @staticmethod
    def __readCurrentVolume() -> int:
        return INITIAL_VOLUME

    @staticmethod
    def __setVolume(newVolume: int):
        print("VOLUME OP: Setting new volume to " + str(newVolume))
        pass

    def __sendCurrentVolume(self):
        msg = IntegerMsg(value=self.volume, fromID=self.id, typeID=MsgID.CURRENT_VOL_INFO, groupID=GroupID.UI)
        self.dispatcher.distribute(msg, self.id)
