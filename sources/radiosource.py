from typing import TYPE_CHECKING, Optional, List

from treelib import Node, Tree
from unidecode import unidecode

from moduleid import ModuleID
from msgs.nodemsg import NodeID, NodeItem
from sources.mpvtreesource import MPVTreeSource
from sources.radioplaylist import RadioPlaylist, PLAYLIST_FILENAME, RadioItem

if TYPE_CHECKING:
    from dispatcher import Dispatcher


class RadioSource(MPVTreeSource[Node]):
    def __init__(self, dispatcher: 'Dispatcher'):
        self._tree = self._initTree()
        super().__init__(ModuleID.RADIO_SOURCE, dispatcher, monitorTime=False)

    def _getRootNodeItem(self) -> NodeItem:
        return self._getNodeItemForPath(self._getPath(self._tree.root))

    def _isAvailable(self) -> bool:
        # TODO
        return True

    def _getParentPath(self, path: Node) -> Node:
        return self._tree.parent(path.identifier)

    def _isLeaf(self, path: Node) -> bool:
        return path.is_leaf()

    def _isPlayable(self, path: Node) -> bool:
        # only leaves with stream URL
        return isinstance(path.data, RadioItem)

    def _getOrderedChildPaths(self, path: Node) -> List[Node]:
        return self._tree.children(path.identifier)

    def _getRootPath(self) -> Node:
        return self._getPath(self._tree.root)

    def _getID(self, path: Node) -> NodeID:
        return path.identifier

    def _getPath(self, nodeID: NodeID) -> Optional[Node]:
        return self._tree.get_node(nodeID)

    def _getNodeLabelFor(self, path: Node) -> str:
        # UNICODE -> ASCII
        return unidecode(path.data.name)

    def _getTrackLabelFor(self, path: Node) -> str:
        # UNICODE -> ASCII
        return unidecode(path.data.name)

    def _playNode(self, nodeID: NodeID) -> None:
        node = self._getPath(nodeID)
        if isinstance(node.data, RadioItem):
            item = node.data  # type: RadioItem
            self._startPlayback(item.url)

    def timePosWasChanged(self, timePos: int):
        # ignored
        pass

    @staticmethod
    def _initTree() -> Tree:
        return RadioPlaylist(PLAYLIST_FILENAME).loadTreeFromFile()

    def _getPathFor(self, mpvPath: str) -> Optional[Node]:
        # checking nodes sequentially :-(
        for node in self._tree.all_nodes():
            if isinstance(node.data, RadioItem):
                item = node.data  # type: RadioItem
                if item.url == mpvPath:
                    return node
        return None
