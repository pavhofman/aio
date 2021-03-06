import logging
from typing import List, TYPE_CHECKING

from groupid import GroupID
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from sources.sourcestatus import SourceStatus
from uis.hassourceparts import HasSourceParts
from uis.sourcepart import SourcePart

if TYPE_CHECKING:
    from dispatcher import Dispatcher

'''
UI 
'''


class ConsoleUI(MsgConsumer, HasSourceParts):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, name: str, dispatcher: 'Dispatcher'):
        MsgConsumer.__init__(self, id=id, name=name, dispatcher=dispatcher)
        HasSourceParts.__init__(self)
        self._volume = 0

    # consuming the message
    def _consume(self, msg: 'Message'):
        logging.debug(self.__class__.__name__ + " received msg: " + msg.__str__())
        if msg.typeID == MsgID.CURRENT_VOL_INFO:
            msg = msg  # type: IntegerMsg
            self._handleVolMsg(msg)
        elif msg.typeID == MsgID.SOURCE_STATUS_INFO:
            msg = msg  # type: IntegerMsg
            self._handleSourceStatusMsg(msg)

    def _handleVolMsg(self, msg: IntegerMsg):
        newVolume = msg.value
        if self._volume != newVolume:
            self._volume = newVolume
            logging.debug("Changed volume to: " + str(self._volume))

    def _handleSourceStatusMsg(self, msg: IntegerMsg):
        source = self._getSourcePartFor(msg)
        if source is not None:
            newStatus = SourceStatus(msg.value)
            source.setStatus(newStatus)

    def _initSourceParts(self) -> List['SourcePart']:
        return [
            SourcePart(id=self.id, dispatcher=self.dispatcher, sourceID=ModuleID.ANALOG_SOURCE),
            SourcePart(id=self.id, dispatcher=self.dispatcher, sourceID=ModuleID.FILE_SOURCE),
            SourcePart(id=self.id, dispatcher=self.dispatcher, sourceID=ModuleID.RADIO_SOURCE),
            SourcePart(id=self.id, dispatcher=self.dispatcher, sourceID=ModuleID.CD_SOURCE)
        ]

    def _getGroupIDs(self) -> List[GroupID]:
        return [GroupID.UI]
