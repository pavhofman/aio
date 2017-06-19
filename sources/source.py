import abc
import logging

from dispatcher import Dispatcher
from groupid import GroupID
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from sourcestatus import SourceStatus


class Source(MsgConsumer, abc.ABC):
    """
    Source representation. Only one instance for each source within the network
    """

    def __init__(self, id: ModuleID, dispatcher: Dispatcher, initStatus=SourceStatus.UNAVAILABLE):
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher)
        self.status = initStatus

    # consuming the message
    def _consume(self, msg: 'Message'):
        logging.debug(str(self) + " received msg" + msg.toString())
        if msg.typeID == MsgID.REQ_SOURCE_STATUS:
            self.__sendSourceStatus()
        elif msg.typeID == MsgID.SET_SOURCE_STATUS:
            msg = msg  # type: IntegerMsg
            newStatus = SourceStatus(msg.value)
            self._setSourceStatus(newStatus)
        elif msg.typeID == MsgID.ACTIVATE_SOURCE:
            msg = msg  # type: IntegerMsg
            self._handleActivateMsg(msg)

    def __sendSourceStatus(self):
        msg = IntegerMsg(value=self._getStatus().value, fromID=self.id, typeID=MsgID.SOURCE_STATUS_INFO,
                         groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    def _getStatus(self) -> SourceStatus:
        return self.status

    def _setSourceStatus(self, newStatus: SourceStatus):
        if self.status != newStatus:
            # changing
            self.status = newStatus
            # informing
            self.__sendSourceStatus()

    def _handleActivateMsg(self, msg: IntegerMsg):
        if msg.value == self.id.value:
            # activate myself
            if self.status.isAvailable():
                if self._activate():
                    self.__sendSourceStatus()
        else:
            # activate some other source, i.e. deactivate myself if active
            if self.status.isSelected():
                if self._deactive():
                    self.__sendSourceStatus()

    @abc.abstractmethod
    def _activate(self) -> bool:
        """
        Activates the source.
        :return: if status changed
        """
        pass

    def _deactive(self) -> bool:
        """
        Deactivates the source.
        :return: if status changed
        """
        # TODO - pretizit v potomcich
        self.status = SourceStatus.NOT_SELECTED
        return True
