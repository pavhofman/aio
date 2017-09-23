import abc
from time import sleep
from typing import TYPE_CHECKING, Optional, Tuple, List, TypeVar, Generic

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

PATH = TypeVar('PATH')


class MPVTreeSource(TreeSource, UsesMPV, Generic[PATH]):
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher', monitorTime: bool):
        self._rootNode = None
        self._playedNodeID = NON_EXISTING_NODE_ID  # type: NodeID
        TreeSource.__init__(self, id=id, dispatcher=dispatcher)
        UsesMPV.__init__(self, monitorTime=monitorTime)

    def _initializeInThread(self):
        self._rootNode = self._getRootNodeItem()
        super()._initializeInThread()

    def _changePlaybackTo(self, playback: PlaybackStatus):
        UsesMPV._changePlaybackTo(self, playback)
        pass

    def _determinePlayback(self) -> PlaybackStatus:
        return UsesMPV._determinePlayback(self)

    def _tryToActivate(self) -> bool:
        # no track selected, stopped
        UsesMPV.reInit(self)
        return True

    def _deactive(self) -> bool:
        UsesMPV.close(self)
        return TreeSource._deactive(self)

    def close(self):
        TreeSource.close(self)
        UsesMPV.close(self)

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

    def chapterWasChanged(self, chapter: int):
        pass

    def _switchedToNewPath(self, path: PATH):
        UsesMPV._resetTimePosTimer(self)
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
        self._sendPlaybackInfo(PlaybackStatus.PAUSED if pause else PlaybackStatus.PLAYING)
        pass

    def timePosWasChanged(self, timePos: int):
        if timePos is not None and self._playedNodeID != NON_EXISTING_NODE_ID:
            duration = self._getDuration()
            duration = duration if duration is not None else 0
            msg = BiIntegerMsg(value1=timePos, value2=duration, fromID=self.id, typeID=MsgID.TIME_POS_INFO,
                               groupID=GroupID.UI)
            self.dispatcher.distribute(msg)

    def pathWasChanged(self, mpvPath: Optional[str]):
        if mpvPath is None:
            self._sendPlaybackInfo(PlaybackStatus.STOPPED)
        else:
            path = self._getPathFor(mpvPath)
            if path is not None and self._isPlayable(path):
                self._switchedToNewPath(path)

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
