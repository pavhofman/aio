import logging
import urllib
from typing import TYPE_CHECKING, Optional, List, Dict

from treelib import Node, Tree
from unidecode import unidecode

from metadata import Metadata
from moduleid import ModuleID
from msgs.nodemsg import NodeID, NodeItem
from sources import playlistparsers
from sources.mpvtreesource import MPVTreeSource
from sources.playbackstatus import PlaybackStatus
from sources.radioplaylist import RadioPlaylist, PLAYLIST_FILENAME, RadioItem

if TYPE_CHECKING:
    from dispatcher import Dispatcher


class RadioSource(MPVTreeSource[Node]):
    def __init__(self, dispatcher: 'Dispatcher'):
        self._tree = None
        # XML tree must be loaded in the thread so that this constructor exits fast
        super().__init__(ModuleID.RADIO_SOURCE, dispatcher, monitorTime=False)

    def _initializeInThread(self):
        self._tree = self._initTree()
        super()._initializeInThread()

    def _getRootNodeItem(self) -> NodeItem:
        return self._getNodeItemForPath(self._getPath(self._tree.root))

    def _isAvailable(self) -> bool:
        return self._tree is not None

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
            streamUrl = self._extractStreamUrl(item.url)
            if streamUrl is not None:
                self._startPlayback(item.url)
            else:
                # not much we can do, stopping playback
                self._changePlaybackTo(PlaybackStatus.STOPPED)

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

    @staticmethod
    def _extractStreamUrl(playlistUrl: str) -> Optional[str]:
        logging.debug("Extracting streams for playlistUrl " + playlistUrl)
        try:
            # noinspection PyUnresolvedReferences
            response = urllib.request.urlopen(playlistUrl, timeout=2)
            if response is not None:
                info = response.info()
                contentType = info.get_content_type()
                print(contentType)  # -> text/html
                print(info.get_content_maintype())  # -> text
                print(info.get_content_subtype())  # -> html
                if contentType == "audio/mpeg":
                    return playlistUrl
                else:
                    contents = response.read()
                    streams = playlistparsers.parse(contents)  # type: List[str]
                    if len(streams) > 0:
                        streamUrl = streams[0]
                        logging.debug("Extracted stream URL " + streamUrl + " from playlistUrl " + playlistUrl)
                        return streamUrl
        except Exception as error:
            logging.error('Data not retrieved because %s\nURL: %s', error, playlistUrl)
        logging.debug("Extracted NO stream URL from playlistUrl " + playlistUrl)
        return None

    def _areEqual(self, path1: Node, path2: Node) -> bool:
        return path1.identifier == path2.identifier

    def _getMetadataParserRules(self) -> Dict[Metadata, List[str]]:
        return {
            Metadata.TITLE: ["icy-title"],
            Metadata.BITRATE: ["icy-br"],
        }
