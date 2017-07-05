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

    def _activate(self) -> bool:
        # no track selected, stopped
        self.status = SourceStatus.STOPPED
        return True

    def _sendNodeInfo(self, nodeID: NodeID, fromIndex: int) -> None:
        nodeID, path = self._getExistingNodeIDAndPath(nodeID)
        self._sendNodeInfoForPath(path, nodeID, fromIndex)

    def _sendNodeInfoForPath(self, path, nodeID, fromIndex):
        nodeItem = self._getNodeItem(nodeID, path)
        rootLabel, totalParents, parentID = self._getParentsData(path)
        children, totalChildren = self._findChildren(path, fromIndex)
        struct = NodeStruct(node=nodeItem,
                            rootLabel=rootLabel,
                            totalParents=totalParents,
                            parentID=parentID,
                            children=children,
                            fromChildIndex=fromIndex,
                            totalChildren=totalChildren)
        msg = NodeMsg(nodeStruct=struct, fromID=self.id, typeID=MsgID.NODE_INFO, groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    def _sendParentNodeInfo(self, nodeID: NodeID) -> None:
        nodeID, path = self._getExistingNodeIDAndPath(nodeID)
        if path.__eq__(ROOT_PATH):
            self._sendNodeInfoForPath(path, nodeID, 0)
        else:
            parentPath = path.parent
            index, total = self._findIndexOfPath(path, parentPath)
            fromIndex = self._calculateFromIndex(index, total)
            parentID = self._getID(parentPath)
            self._sendNodeInfoForPath(parentPath, parentID, fromIndex)

    def _findIndexOfPath(self, path: Path, parentPath: Path) -> (int, int):
        index = 0
        orderedPaths = self._getOrderedChildPaths(parentPath)
        for childPath in orderedPaths:
            if childPath.__eq__(path):
                return index, len(orderedPaths)
            index += 1
        return 0, len(orderedPaths)

    def _findChildren(self, path: Path, fromIndex: int) -> Tuple[List[NodeItem], int]:
        index = 0
        total = 0
        childrenCount = 0
        children = []  # type: List[NodeItem]
        if path.is_dir():
            # sorted by case insensitive name
            for childPath in self._getOrderedChildPaths(path):
                if (index >= fromIndex) and (childrenCount < MAX_CHILDREN):
                    children.append(self._getNodeItem(self._getID(childPath), childPath))
                    childrenCount += 1
                index += 1
                total += 1
        return children, total

    def _getOrderedChildPaths(self, path) -> List[Path]:
        return sorted(path.iterdir(), key=lambda k: str(k).lower())

    def _getNodeItem(self, nodeID: NodeID, path: Path):
        isLeaf = path.is_file() or all(False for _ in path.iterdir())
        return NodeItem(nodeID=nodeID, label=self._getLabelFor(path), isPlayable=True,
                        isLeaf=isLeaf)

    def _getExistingNodeIDAndPath(self, nodeID: NodeID) -> Tuple[NodeID, Path]:
        if nodeID == 0:
            path = Path(ROOT_PATH)
            nodeID = self._getID(path)
        else:
            path = self._getPath(nodeID)
            if path is None:
                path = Path(ROOT_PATH)
                nodeID = self._getID(path)
        return nodeID, path

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

    def _getPath(self, itemID: NodeID) -> Optional[Path]:
        if itemID in self._pathsByID.keys():
            return self._pathsByID[itemID]
        else:
            return None

    def _getParentsData(self, path: Path) -> (str, int, NodeID):
        if path.__eq__(ROOT_PATH):
            # directly root
            return ROOT_PATH.name, 0, NON_EXISTING_NODE_ID
        else:
            parentPath = path.parent  # type: Path
            directParentID = self._getID(parentPath)
            totalParents = 1  # type: int
            while not parentPath.__eq__(ROOT_PATH):
                parentPath = parentPath.parent
                totalParents += 1
            return ROOT_PATH.name, totalParents, directParentID

    @staticmethod
    def _getLabelFor(path: Path) -> str:
        # UNICODE -> ASCII
        return unidecode(path.name)
