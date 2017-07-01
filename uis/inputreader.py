import logging
from typing import Optional, List

import exiting
import msgconsumer
from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from msgs.requestmsg import RequestMsg
from uis.abstractreader import AbstractReader


class InputReader(AbstractReader):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, module: msgconsumer.MsgConsumer):
        self.id = id
        self._module = module
        super().__init__()

    def _readMsg(self) -> Optional['Message']:
        line = input("READER ID " + str(self.id) + ": Enter msg:\n")
        parts = line.split()  # type: List[str]
        if len(parts) > 0:
            if parts[0] == 'E':
                exiting.exitCleanly(0)
            elif parts[0].isdigit():
                msg = self._formatMessage(parts)
                if msg is not None:
                    return msg

        logging.warning("Unknown command " + line)
        return None

    def _formatMessage(self, parts: List[str]) -> Optional['Message']:
        msgID = int(parts[0])
        if msgID == MsgID.SET_VOL.value:
            volume = int(parts[1])
            return IntegerMsg(value=volume, fromID=self.id, typeID=MsgID.SET_VOL, forID=ModuleID.VOLUME_OPERATOR)

        elif msgID == MsgID.REQ_CURRENT_VOL_INFO.value:
            return RequestMsg(self.id, typeID=MsgID.REQ_CURRENT_VOL_INFO, forID=ModuleID.VOLUME_OPERATOR)
        if msgID == MsgID.SET_SOURCE_STATUS.value:
            sourceID = int(parts[1])
            statusID = int(parts[2])
            return IntegerMsg(value=statusID, fromID=self.id, typeID=MsgID.SET_SOURCE_STATUS,
                              forID=ModuleID(sourceID))

        elif msgID == MsgID.REQ_SOURCE_STATUS.value:
            return RequestMsg(self.id, typeID=MsgID.REQ_SOURCE_STATUS, groupID=GroupID.SOURCE)
        if msgID == MsgID.ACTIVATE_SOURCE.value:
            sourceID = int(parts[1])
            return IntegerMsg(value=sourceID, fromID=self.id, typeID=MsgID.ACTIVATE_SOURCE, groupID=GroupID.SOURCE)
        else:
            return None

    def _processMsg(self, msg: 'Message'):
        self._module.dispatcher.distribute(msg)
