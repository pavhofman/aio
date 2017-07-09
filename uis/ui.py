import abc
import logging
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from sourcestatus import SourceStatus
from uis.hassourceparts import HasSourceParts

if TYPE_CHECKING:
    from dispatcher import Dispatcher

'''
UI 
'''


# noinspection PyAbstractClass
class UI(MsgConsumer, HasSourceParts, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher'):
        # call the thread class
        MsgConsumer.__init__(self, id=id, dispatcher=dispatcher)
        HasSourceParts.__init__(self)
        self._volume = 0

    def stop(self):
        super().stop()

    # consuming the message

    def _consume(self, msg: 'Message'):
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

    def close(self):
        super().close()

    def _handleSourceStatusMsg(self, msg: IntegerMsg):
        source = self._getSourcePartFor(msg)
        if source is not None:
            newStatus = SourceStatus(msg.value)
            if newStatus != source.status:
                source.status = newStatus
                if newStatus.isActivated():
                    self.activeSource = source
                logging.debug("Changed status of UI Source " + source.__class__.__name__ + " to " + str(source.status))
