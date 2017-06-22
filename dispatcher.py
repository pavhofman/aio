import logging
from typing import TYPE_CHECKING

import globalvars
from errors import ParameterError
from groupid import GroupID
from moduleid import ModuleID
from msgs.message import Message

if TYPE_CHECKING:
    from msgconsumer import MsgConsumer
"""
Message dispatcher
"""


class Dispatcher:
    def __init__(self, name, routeMap: dict, groupMap: dict):
        # call the thread class
        super().__init__()
        self.name = name
        self.routeMap = routeMap
        self.groupMap = groupMap
        self.msgCount = 0

    # distributing the message
    def distribute(self, msg: 'Message', excludeID=None):
        if msg.forID is not ModuleID.ANY:
            targetID = self.routeMap[msg.forID]
            # checking just in case
            if targetID is not None:
                self._submitToTargetID(msg, targetID)
        elif msg.groupID is not GroupID.ANY:
            for targetID in self.groupMap[msg.groupID]:
                if targetID != excludeID:
                    self._submitToTargetID(msg, targetID)

    def _submitToTargetID(self, msg, targetID):
        if msg.fromID == targetID:
            logging.warning("Trying to send msg " + msg.toString() + " to originator, skipping")
            return

        consumer = getMsgConsumer(targetID)
        if consumer is not None:
            consumer.receive(msg)
            # increment message counter
            self.msgCount += 1

    def printStats(self):
        print("Dispatcher " + self.name + ": " + str(self.msgCount))


# noinspection PyShadowingBuiltins
def getMsgConsumer(id: ModuleID) -> 'MsgConsumer':
    for consumer in globalvars.msgConsumers:
        if consumer.id == id:
            return consumer
    raise ParameterError("Unknown module ID " + str(id))
