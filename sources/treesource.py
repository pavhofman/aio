import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg, IntegerMsg
from msgs.message import Message
from msgs.nodemsg import NodeID
from sources.source import Source

if TYPE_CHECKING:
    from dispatcher import Dispatcher

# how many children nodes to send in NodesStruct - should correspond to number of nodes displayed in UI
MAX_CHILDREN = 5
# how many singling nodes will be displayed before current node in parent request
PREVIOUS_SIBLINGS = 2


class TreeSource(Source, abc.ABC):
    """
    Source representation. Only one instance for each source within the network
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher'):
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher)

    # consuming the message
    def _consume(self, msg: 'Message') -> bool:
        if not super()._consume(msg):
            if msg.typeID == MsgID.REQ_NODE:
                msg = msg  # type: BiIntegerMsg
                self._sendNodeInfo(msg.value1, msg.value2)
                return True
            elif msg.typeID == MsgID.REQ_PARENT_NODE:
                msg = msg  # type: IntegerMsg
                self._sendParentNodeInfo(msg.value)
                return True
            elif msg.typeID == MsgID.PLAY_NODE:
                msg = msg  # type: IntegerMsg
                self._playNode(msg.value)
                return True
        else:
            return False

    def _calculateFromIndex(self, nodeIndex: int, total: int) -> int:
        """
        :param nodeIndex: index of same-level node
        :param total: total of nodes on that level
        :return: calculated fromIndex
        """
        if nodeIndex - PREVIOUS_SIBLINGS + MAX_CHILDREN > total:
            # upper limit - always max_children shown
            fromIndex = total - MAX_CHILDREN
        else:
            # windowed
            fromIndex = nodeIndex - PREVIOUS_SIBLINGS
        # lower limit = 0
        return fromIndex if fromIndex >= 0 else 0

    @abc.abstractmethod
    def _sendNodeInfo(self, nodeID: NodeID, fromIndex: int) -> None:
        pass

    @abc.abstractmethod
    def _sendParentNodeInfo(self, nodeID: NodeID) -> None:
        pass

    @abc.abstractmethod
    def _playNode(self, nodeID: NodeID) -> None:
        pass
