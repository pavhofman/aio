import logging
from typing import TYPE_CHECKING, DefaultDict, List, Iterator

import globalvars
from errors import ParameterError
from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message

if TYPE_CHECKING:
    from msgconsumer import MsgConsumer
"""
Message dispatcher
"""

log = logging.getLogger("dispatcher")
log.setLevel(logging.DEBUG)


class Dispatcher:
    def __init__(self, name, gatewayIDs: List[ModuleID]):
        # call the thread class
        super().__init__()
        self.name = 'Dispatcher ' + name
        self._gatewayIDs = gatewayIDs
        self._routeMap = self._initRouteMap(gatewayIDs)  # type: DefaultDict[ModuleID, ModuleID]
        self._groupMap = {}  # type: DefaultDict[GroupID, List[ModuleID]]
        self._msgCount = 0

    def _initRouteMap(self, gatewayIDs: List[ModuleID]) -> DefaultDict[ModuleID, ModuleID]:
        """
        Initial filling the route map with gateways
        """
        routeMap = {}
        for gatewayID in gatewayIDs:
            routeMap[gatewayID] = gatewayID
        return routeMap

    def distribute(self, msg: Message, senderID: ModuleID):
        """
        Distributing the message.
        :param senderID: bordering sender. Not the original sender (stored in msg.fromID)!
        """
        log.debug(self.name + ": from sender " + str(getMsgConsumer(senderID)) + ": " + str(msg))
        self._updateRouteMap(msg, senderID)
        if msg.typeID == MsgID.IN_GROUPS_MSG:
            msg = msg  # type: IntegerMsg
            self._updateGroupMap(msg.value, senderID)
            self._distributeToGateways(msg, senderID)
        elif msg.forID is not ModuleID.ANY and msg.forID in self._routeMap.keys():
            self._distributeToForID(msg)
        elif msg.groupID is not GroupID.ANY and msg.groupID in self._groupMap.keys():
            self._distributeToGroupID(msg, senderID)
        else:
            # no specific targets found, sending to all gateways
            self._distributeToGateways(msg, senderID)

    def _distributeToGroupID(self, msg, senderID):
        for targetID in self._groupMap[msg.groupID]:
            if targetID != senderID:
                self._submitToTargetID(msg, targetID)

    def _distributeToForID(self, msg):
        targetID = self._routeMap[msg.forID]  # type: ModuleID
        # checking just in case
        if targetID is not None:
            self._submitToTargetID(msg, targetID)

    def _updateRouteMap(self, msg: Message, senderID: ModuleID) -> None:
        if msg.fromID not in self._routeMap.keys():
            self._routeMap[msg.fromID] = senderID

    def _updateGroupMap(self, encodedGroupIDs: int, senderID: ModuleID) -> None:
        for groupID in decodeGroupIDs(encodedGroupIDs):
            if groupID not in self._groupMap.keys():
                self._groupMap[groupID] = []
            if senderID not in self._groupMap[groupID]:
                self._groupMap[groupID].append(senderID)

    def _distributeToGateways(self, msg: Message, senderID: ModuleID):
        # distribute to all other gateways
        for gatewayID in self._gatewayIDs:
            if senderID != gatewayID:
                self._submitToTargetID(msg, gatewayID)

    def _submitToTargetID(self, msg: Message, targetID):
        if msg.fromID == targetID:
            logging.warning("Trying to send msg " + msg.__str__() + " to originator, skipping")
            return

        consumer = getMsgConsumer(targetID)
        if consumer is not None:
            consumer.receive(msg)
            log.debug(self.name + ": to: " + str(consumer) + " submitted " + str(msg))
            # increment message counter
            self._msgCount += 1

    def printStats(self):
        print(str(self) + ": " + str(self._msgCount))

    def __str__(self) -> str:
        return "Dispatcher " + self.name


# noinspection PyShadowingBuiltins
def getMsgConsumer(id: ModuleID) -> 'MsgConsumer':
    # wait untill all consumers are instantiated
    globalvars.consumersReadyEvent.wait()
    for consumer in globalvars.msgConsumers:
        if consumer.id == id:
            return consumer
    raise ParameterError("Unknown module ID " + str(id))


def bits(number: int) -> Iterator[int]:
    bit = 1
    position = 0
    while number >= bit:
        if number & bit:
            yield position
        bit <<= 1
        position += 1


def decodeGroupIDs(value: int) -> List[GroupID]:
    return list(GroupID(groupValue) for groupValue in bits(value))


def encodeGroupIDs(groupIDs: List[GroupID]) -> int:
    result = 0
    for groupID in groupIDs:
        result |= 1 << groupID.value
    return result
