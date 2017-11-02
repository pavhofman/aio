import time
from typing import TYPE_CHECKING

from groupid import GroupID
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgid import MsgID
from msgs.message import Message
from msgs.requestmsg import RequestMsg

if TYPE_CHECKING:
    from dispatcher import Dispatcher

"""
Heartbeat thread periodically requesting status updates 
"""


class Heartbeat(MsgConsumer):
    def __init__(self, dispatcher: 'Dispatcher'):
        # call the thread class
        super().__init__(id=ModuleID.HEARTBEAT, dispatcher=dispatcher)

    # noinspection PyShadowingNames
    def run(self):
        while not self.stopped():
            time.sleep(2)
            msg = RequestMsg(ModuleID.HEARTBEAT, typeID=MsgID.REQ_SOURCE_STATUS, groupID=GroupID.SOURCE)
            self.dispatcher.distribute(msg, self.id)
            msg = RequestMsg(ModuleID.HEARTBEAT, typeID=MsgID.REQ_CURRENT_VOL_INFO, forID=ModuleID.VOLUME_OPERATOR)
            self.dispatcher.distribute(msg, self.id)
            # only one run during development
            self.stop()

    def _consume(self, msg: 'Message') -> bool:
        # never called
        pass
