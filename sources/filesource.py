from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from time import sleep
from typing import TYPE_CHECKING, Optional, Dict, Tuple, List

from unidecode import unidecode

from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg
from msgs.nodemsg import NodeMsg, NodeItem, NodeID, NON_EXISTING_NODE_ID, NodeStruct
from msgs.trackmsg import TrackMsg, TrackItem
from sources.playbackstatus import PlaybackStatus
from sources.treesource import TreeSource, MAX_CHILDREN
from sources.usesmpv import UsesMPV

if TYPE_CHECKING:
    from dispatcher import Dispatcher

ROOT_PATH = Path("/home/pavel/Hudba")
# maximum directory depth for recursive loadfile
MAX_DIR_DEPTH = 20


@contextmanager
def locked(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


class FileSource(TreeSource, UsesMPV):
    def __init__(self, dispatcher: 'Dispatcher'):
        self._myLock = Lock()
        self._pathsByID = {}  # type: Dict[NodeID, Path]
        self._idsByPathStr = {}  # type: Dict[str, NodeID]
        self._lastNodeID = 0
        self._rootNode = None
        self._playedNodeID = NON_EXISTING_NODE_ID  # type: NodeID
        TreeSource.__init__(self, id=ModuleID.FILE_SOURCE, dispatcher=dispatcher)
        UsesMPV.__init__(self)
        self._rootNode = self._getNodeItemForPath(ROOT_PATH)

    def _changePlaybackTo(self, playback: PlaybackStatus):
        UsesMPV._changePlaybackTo(self, playback)
        pass

    def _determinePlayback(self) -> PlaybackStatus:
        return UsesMPV._determinePlayback(self)

    def _isAvailable(self) -> bool:
        # TODO
        return True

    def _tryToActivate(self) -> bool:
        # no track selected, stopped
        self._acquireMPV()
        return True

    def _deactive(self) -> bool:
        self._releaseMPV()
        return TreeSource._deactive(self)

    def close(self):
        TreeSource.close(self)
        UsesMPV.close(self)

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
        msg = NodeMsg(nodeStruct=struct, fromID=self.id, groupID=GroupID.UI)
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
            return NodeItem(nodeID=nodeID, label=self._getNodeLabelFor(path), isPlayable=True,
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
    def _getNodeLabelFor(path: Path) -> str:
        # UNICODE -> ASCII
        # only basename
        return unidecode(path.name)

    @staticmethod
    def _getTrackLabelFor(path: Path) -> str:
        # fullname incl path from ROOT excl
        fullname = str(path)[len(str(ROOT_PATH)):].lstrip('/')
        # UNICODE -> ASCII
        return unidecode(fullname)

    def _playNode(self, nodeID: NodeID) -> None:
        path = self._getPath(nodeID)
        if path is not None:
            self._loadFilesToMPV(path)

    def chapterWasChanged(self, chapter: int):
        pass

    def pathWasChanged(self, filePath: Optional[str]):
        if filePath is None:
            self._sendPlaybackInfo(PlaybackStatus.STOPPED)
        else:
            path = Path(filePath)
            if path.is_file():
                self._switchedToNewFilePath(filePath, path)

    def _switchedToNewFilePath(self, filePath: str, path: Path):
        UsesMPV.pathWasChanged(self, filePath)
        self._playedNodeID = self._getID(path)
        # waiting for duration being available by mpv
        # ugly hack
        sleep(0.05)
        # send msg
        trackItem = TrackItem(nodeID=self._playedNodeID, label=self._getTrackLabelFor(path), descr="")
        msg = TrackMsg(trackItem=trackItem, fromID=self.id, groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    def metadataWasChanged(self, metadata: dict):
        pass

    def pauseWasChanged(self, pause: bool):
        UsesMPV.pauseWasChanged(self, pause)
        pass

    def timePosWasChanged(self, timePos: int):
        if timePos is not None and self._playedNodeID != NON_EXISTING_NODE_ID:
            duration = self._getDuration()
            duration = duration if duration is not None else 0
            msg = BiIntegerMsg(value1=timePos, value2=duration, fromID=self.id, typeID=MsgID.TIME_POS_INFO,
                               groupID=GroupID.UI)
            self.dispatcher.distribute(msg)

    def _loadFilesToMPV(self, path: Path) -> None:
        """
        Will call mpv command loadfile with current path + respective sub paths
        We cannot pass just directory to MPV because we cannot control order of played items in subdirectory.
        But the playback order must correspond to displayed order - generated by _getOrderedChildPaths(path)
        Depth of directory traversal is limited with MAX_DIR_DEPTH
        """
        # loadfile command starts playback immediately

        if path.is_dir():
            self._appendChildrenToMPV(path, True, 0)
        else:
            self._startPlayback(str(path))

    def _appendChildrenToMPV(self, path: Path, firstToPlay: bool, level: int) -> None:
        """
        Recursive method for adding files in subtree to mpv playlist
        :param path: directory path
        :param firstToPlay: the first to-be-played track is played with startPlayback,
        all subsequent with appendToPlayback
        :param level: currect directory traversal depth
        """
        # sorted by case insensitive name
        for childPath in self._getOrderedChildPaths(path):
            if childPath.is_file():
                if firstToPlay:
                    self._startPlayback(str(childPath))
                    firstToPlay = False
                else:
                    self._appendToPlayback(str(childPath))
            elif level < MAX_DIR_DEPTH:
                self._appendChildrenToMPV(childPath, firstToPlay, level + 1)
