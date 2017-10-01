import abc
from typing import TYPE_CHECKING, TypeVar, List, Optional, Generic, Tuple

from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg, IntegerMsg
from msgs.message import Message
from msgs.nodemsg import NodeID, NON_EXISTING_NODE_ID, NodeItem, NodeStruct, NodeMsg
from sources.source import Source

if TYPE_CHECKING:
    from dispatcher import Dispatcher

# how many children nodes to send in NodesStruct - should correspond to number of nodes displayed in UI
MAX_CHILDREN = 5
# how many singling nodes will be displayed before current node in parent request
PREVIOUS_SIBLINGS = 2

PATH = TypeVar('PATH')


class TreeSource(Source, abc.ABC, Generic[PATH]):
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
                if self._status.isAvailable():
                    msg = msg  # type: BiIntegerMsg
                    self._sendNodeInfo(msg.value1, msg.value2)
                return True
            elif msg.typeID == MsgID.REQ_PARENT_NODE:
                if self._status.isAvailable():
                    msg = msg  # type: IntegerMsg
                    self._sendParentNodeInfo(msg.value)
                return True
            elif msg.typeID == MsgID.PLAY_NODE:
                if self._status.isAvailable():
                    msg = msg  # type: IntegerMsg
                    self._playNode(msg.value)
                return True
        else:
            return False

    def _sendNodeInfo(self, nodeID: NodeID, fromIndex: int) -> None:
        nodeID = self._getExistingNodeID(nodeID)
        path = self._getPath(nodeID)  # type: PATH
        nodeItem = self._createNodeItem(nodeID, path)
        totalParents, parentID = self._getParentsTotalAndID(path)
        children, totalChildren = self._findChildrenAndTotal(path, fromIndex)
        struct = NodeStruct(node=nodeItem,
                            rootNode=self._rootNode,
                            totalParents=totalParents,
                            parentID=parentID,
                            children=children,
                            fromChildIndex=fromIndex,
                            totalChildren=totalChildren)
        msg = NodeMsg(nodeStruct=struct, fromID=self.id, groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    def _sendParentNodeInfo(self, nodeID: NodeID) -> None:
        nodeID = self._getExistingNodeID(nodeID)
        if nodeID == self._rootNode.nodeID:
            self._sendNodeInfo(self._rootNode.nodeID, 0)
        else:
            path = self._getPath(nodeID)
            parentPath = self._getParentPath(path)
            index, total = self._findIndexOfPath(path, parentPath)
            fromIndex = self._calculateFromIndex(index, total)
            parentID = self._getID(parentPath)
            self._sendNodeInfo(parentID, fromIndex)

    def _findIndexOfPath(self, path: PATH, parentPath: PATH) -> (int, int):
        index = 0
        orderedPaths = self._getOrderedChildPaths(parentPath)
        for childPath in orderedPaths:
            if self._areEqual(childPath, path):
                return index, len(orderedPaths)
            index += 1
        return 0, len(orderedPaths)

    def _findChildrenAndTotal(self, path: PATH, fromIndex: int) -> Tuple[List[NodeItem], int]:
        index = 0
        total = 0
        childrenCount = 0
        children = []  # type: List[NodeItem]
        if not self._isLeaf(path):
            # sorted by case insensitive name
            for childPath in self._getOrderedChildPaths(path):
                if (index >= fromIndex) and (childrenCount < MAX_CHILDREN):
                    children.append(self._getNodeItemForPath(childPath))
                    childrenCount += 1
                index += 1
                total += 1
        return children, total

    def _createNodeItemForID(self, nodeID: NodeID) -> NodeItem:
        path = self._getPath(nodeID)
        return self._createNodeItem(nodeID, path)

    def _getNodeItemForPath(self, path: PATH) -> NodeItem:
        nodeID = self._getID(path)
        return self._createNodeItem(nodeID, path)

    def _createNodeItem(self, nodeID: NodeID, path: PATH) -> NodeItem:
        if self._rootNode is not None and nodeID == self._rootNode.nodeID:
            return self._rootNode
        else:
            return NodeItem(nodeID=nodeID, label=self._getNodeLabelFor(path), isPlayable=self._isPlayable(path),
                            isLeaf=self._isLeaf(path))

    def _getExistingNodeID(self, nodeID: NodeID) -> NodeID:
        path = self._getPath(nodeID)
        if path is None:
            return self._rootNode.nodeID
        else:
            return nodeID

    def _getParentsTotalAndID(self, path: PATH) -> Tuple[int, NodeID]:
        rootPath = self._getRootPath()  # type: PATH
        if path.__eq__(rootPath):
            # directly _xmlRoot
            return 0, NON_EXISTING_NODE_ID
        else:
            parentPath = self._getParentPath(path)  # type: PATH
            directParentID = self._getID(parentPath)
            totalParents = 1  # type: int
            while not parentPath.__eq__(rootPath):
                parentPath = self._getParentPath(parentPath)
                totalParents += 1
            return totalParents, directParentID

    @staticmethod
    def _calculateFromIndex(nodeIndex: int, total: int) -> int:
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

    def _initValuesForUnavailable(self):
        self._rootNode = None  # is initialized in makeAvailable
        self._playedNodeID = NON_EXISTING_NODE_ID  # type: NodeID

    def _initValuesForAvailable(self) -> bool:
        self._rootNode = self._getRootNodeItem()
        return super()._initValuesForAvailable()

    def _getPlayedNode(self) -> Optional[PATH]:
        if self._playedNodeID != NON_EXISTING_NODE_ID:
            return self._getPath(self._playedNodeID)
        else:
            return None

    @abc.abstractmethod
    def _playNode(self, nodeID: NodeID) -> None:
        pass

    @abc.abstractmethod
    def _getPathFor(self, filePath: str) -> Optional[PATH]:
        pass

    @abc.abstractmethod
    def _getRootPath(self) -> PATH:
        pass

    @abc.abstractmethod
    def _getNodeLabelFor(self, path: PATH) -> str:
        pass

    @abc.abstractmethod
    def _getTrackLabelFor(self, path: PATH) -> str:
        pass

    @abc.abstractmethod
    def _getID(self, path: PATH) -> NodeID:
        pass

    @abc.abstractmethod
    def _getPath(self, nodeID: NodeID) -> Optional[PATH]:
        pass

    @abc.abstractmethod
    def _getRootNodeItem(self) -> NodeItem:
        pass

    @abc.abstractmethod
    def _getParentPath(self, path: PATH) -> PATH:
        pass

    @abc.abstractmethod
    def _isLeaf(self, path: PATH) -> bool:
        pass

    @abc.abstractmethod
    def _isPlayable(self, path: PATH) -> bool:
        pass

    @abc.abstractmethod
    def _getOrderedChildPaths(self, path: PATH) -> List[PATH]:
        pass

    @abc.abstractmethod
    def _areEqual(self, path1: PATH, path2: PATH) -> bool:
        pass
