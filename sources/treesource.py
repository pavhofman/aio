import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg
from msgs.message import Message
from msgs.nodemsg import NodeID
from sources.source import Source
from sourcestatus import SourceStatus

if TYPE_CHECKING:
    from dispatcher import Dispatcher


class TreeSource(Source, abc.ABC):
    """
    Source representation. Only one instance for each source within the network
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher', initStatus=SourceStatus.UNAVAILABLE):
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher, initStatus=initStatus)

    # consuming the message
    def _consume(self, msg: 'Message') -> bool:
        if not super()._consume(msg):
            if msg.typeID == MsgID.REQ_NODE:
                msg = msg  # type: BiIntegerMsg
                self._sendNodeInfo(msg.value1, msg.value2)
                return True
        else:
            return False

    @abc.abstractmethod
    def _sendNodeInfo(self, nodeID: NodeID, fromIndex: int) -> None:
        pass
