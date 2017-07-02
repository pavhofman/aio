from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Optional, Dict, Tuple, List

from unidecode import unidecode

from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.nodemsg import NodeMsg, NodeItem, NodeID, NON_EXISTING_NODE_ID, NodeStruct
from sources.nodesource import NodeSource
from sourcestatus import SourceStatus

if TYPE_CHECKING:
    from dispatcher import Dispatcher

ROOT_PATH = Path("/home/pavel/Hudba")
MAX_CHILDREN = 5


@contextmanager
def locked(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


class FileSource(NodeSource):
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
        nodeItem = self._getNodeItem(nodeID, path)
        parentID = self._getParentID(path)

        children, total = self._findChildren(path, fromIndex)
        struct = NodeStruct(node=nodeItem,
                            parentID=parentID,
                            children=children,
                            fromIndex=fromIndex,
                            total=total)
        msg = NodeMsg(nodeStruct=struct, fromID=self.id, typeID=MsgID.NODE_INFO, groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    def _findChildren(self, path: Path, fromIndex: int) -> Tuple[List[NodeItem], int]:
        index = 0
        total = 0
        childrenCount = 0
        children = []  # type: List[NodeItem]
        if path.is_dir():
            # sorted by case insensitive name
            for childPath in sorted(path.iterdir(), key=lambda k: str(k).lower()):
                if (index >= fromIndex) and (childrenCount < MAX_CHILDREN):
                    children.append(self._getNodeItem(self._getID(childPath), childPath))
                    childrenCount += 1
                index += 1
                total += 1
        return children, total

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

    def _getParentID(self, path: Path) -> NodeID:
        if path.__eq__(ROOT_PATH):
            return NON_EXISTING_NODE_ID
        else:
            parent = path.parent  # type: Path
            return self._getID(parent)

    @staticmethod
    def _getLabelFor(path: Path) -> str:
        # UNICODE -> ASCII
        return unidecode(str(path))
