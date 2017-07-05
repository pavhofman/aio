from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Optional, Dict, Tuple, List

from unidecode import unidecode

from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.nodemsg import NodeMsg, NodeItem, NodeID, NON_EXISTING_NODE_ID, NodeStruct
from sources.treesource import TreeSource, MAX_CHILDREN
from sourcestatus import SourceStatus

if TYPE_CHECKING:
    from dispatcher import Dispatcher

ROOT_PATH = Path("/home/pavel/Hudba")


@contextmanager
def locked(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


class FileSource(TreeSource):
    def __init__(self, dispatcher: 'Dispatcher'):
        super().__init__(id=ModuleID.FILE_SOURCE, dispatcher=dispatcher, initStatus=SourceStatus.NOT_ACTIVE)
        self._myLock = Lock()
        self._pathsByID = {}  # type: Dict[NodeID, Path]
        self._idsByPathStr = {}  # type: Dict[str, NodeID]
        self._lastNodeID = 0
        self._rootNode = None
        self._rootNode = self._getNodeItemForPath(ROOT_PATH)

    def _activate(self) -> bool:
        # no track selected, stopped
        self.status = SourceStatus.STOPPED
        return True

    def _sendNodeInfo(self, nodeID: NodeID, fromIndex: int) -> None:
        nodeID = self._getExistingNodeID(nodeID)
        path = self._getPath(nodeID)
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
        msg = NodeMsg(nodeStruct=struct, fromID=self.id, typeID=MsgID.NODE_INFO, groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    def _sendParentNodeInfo(self, nodeID: NodeID) -> None:
        nodeID = self._getExistingNodeID(nodeID)
        if nodeID == self._rootNode.nodeID:
            self._sendNodeInfo(self._rootNode.nodeID, 0)
        else:
            path = self._getPath(nodeID)
            parentPath = path.parent
            index, total = self._findIndexOfPath(path, parentPath)
            fromIndex = self._calculateFromIndex(index, total)
            parentID = self._getID(parentPath)
            self._sendNodeInfo(parentID, fromIndex)

    def _findIndexOfPath(self, path: Path, parentPath: Path) -> (int, int):
        index = 0
        orderedPaths = self._getOrderedChildPaths(parentPath)
        for childPath in orderedPaths:
            if childPath.__eq__(path):
                return index, len(orderedPaths)
            index += 1
        return 0, len(orderedPaths)

    def _findChildrenAndTotal(self, path: Path, fromIndex: int) -> Tuple[List[NodeItem], int]:
        index = 0
        total = 0
        childrenCount = 0
        children = []  # type: List[NodeItem]
        if path.is_dir():
            # sorted by case insensitive name
            for childPath in self._getOrderedChildPaths(path):
                if (index >= fromIndex) and (childrenCount < MAX_CHILDREN):
                    children.append(self._getNodeItemForPath(childPath))
                    childrenCount += 1
                index += 1
                total += 1
        return children, total

    @staticmethod
    def _getOrderedChildPaths(path) -> List[Path]:
        return sorted(path.iterdir(), key=lambda k: str(k).lower())

    def _createNodeItemForID(self, nodeID: NodeID) -> NodeItem:
        path = self._getPath(nodeID)
        return self._createNodeItem(nodeID, path)

    def _getNodeItemForPath(self, path: Path) -> NodeItem:
        nodeID = self._getID(path)
        return self._createNodeItem(nodeID, path)

    def _createNodeItem(self, nodeID: NodeID, path: Path) -> NodeItem:
        if self._rootNode is not None and nodeID == self._rootNode.nodeID:
            return self._rootNode
        else:
            isLeaf = path.is_file() or all(False for _ in path.iterdir())
            return NodeItem(nodeID=nodeID, label=self._getLabelFor(path), isPlayable=True,
                            isLeaf=isLeaf)

    def _getExistingNodeID(self, nodeID: NodeID) -> NodeID:
        path = self._getPath(nodeID)
        if path is None:
            return self._rootNode.nodeID
        else:
            return nodeID

    def _getID(self, path: Path) -> NodeID:
        with locked(self._myLock):
            pathStr = str(path)
            if pathStr in self._idsByPathStr:
                return self._idsByPathStr[pathStr]
            else:
                # add to caches, generate new ID
                self._lastNodeID += 1
                self._pathsByID[self._lastNodeID] = path
                self._idsByPathStr[pathStr] = self._lastNodeID
                return self._lastNodeID

    def _getPath(self, nodeID: NodeID) -> Optional[Path]:
        if nodeID in self._pathsByID.keys():
            return self._pathsByID[nodeID]
        else:
            return None

    def _getParentsTotalAndID(self, path: Path) -> Tuple[int, NodeID]:
        if path.__eq__(ROOT_PATH):
            # directly root
            return 0, NON_EXISTING_NODE_ID
        else:
            parentPath = path.parent  # type: Path
            directParentID = self._getID(parentPath)
            totalParents = 1  # type: int
            while not parentPath.__eq__(ROOT_PATH):
                parentPath = parentPath.parent
                totalParents += 1
            return totalParents, directParentID

    @staticmethod
    def _getLabelFor(path: Path) -> str:
        # UNICODE -> ASCII
        return unidecode(path.name)
