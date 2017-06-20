import time
from threading import Thread, Event

import dispatcher
from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.requestmsg import RequestMsg

"""
Heartbeat thread periodically requesting status updates 
"""


class Heartbeat(Thread):
    # noinspection PyShadowingNames
    def __init__(self, dispatcher: 'dispatcher.Dispatcher'):
        # call the thread class
        super().__init__()
        self.dispatcher = dispatcher
        self.__event = Event()
        self.setDaemon(True)
        # unique ID among modules of same type
        self.start()

    def stop(self):
        self.__event.set()

    def stopped(self) -> bool:
        return self.__event.isSet()

    def run(self):
        while not self.stopped():
            time.sleep(5)
            msg = RequestMsg(ModuleID.HEARTBEAT, typeID=MsgID.REQ_SOURCE_STATUS, groupID=GroupID.SOURCE)
            self.dispatcher.distribute(msg)
            msg = RequestMsg(ModuleID.HEARTBEAT, typeID=MsgID.REQ_CURRENT_VOL_INFO, forID=ModuleID.VOLUME_OPERATOR)
            self.dispatcher.distribute(msg)
            self.stop()

    def close(self):
        self.stop()
