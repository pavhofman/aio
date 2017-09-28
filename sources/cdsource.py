import logging
from typing import TYPE_CHECKING, Optional, List, Dict

import pyudev
from pyudev import Monitor, MonitorObserver, Devices
from treelib import Node, Tree
from unidecode import unidecode

from common.timeutils import secsToTime
from config import DEV_CDROM
from metadata import Metadata
from moduleid import ModuleID
from msgs.nodemsg import NodeID, NodeItem
from sources.cdplaylist import CDPlaylist, TrackItem, RootItem
from sources.mpv import MPVCommandError
from sources.mpvtreesource import MPVTreeSource

if TYPE_CHECKING:
    from dispatcher import Dispatcher

CDDA__MPV_FILEPATH = "cdda://"
MEDIA_TRACK_COUNT_AUDIO_UDEV_TAG = 'ID_CDROM_MEDIA_TRACK_COUNT_AUDIO'
DISK_EJECT_REQUEST_UDEV_TAG = 'DISK_EJECT_REQUEST'
CD_READ_TRIES = 20


class CDSource(MPVTreeSource[Node]):
    def __init__(self, dispatcher: 'Dispatcher'):
        self.__chapterToSwitch = None  # type: Optional[int]
        super().__init__(ModuleID.CD_SOURCE, dispatcher, monitorTime=True)
        self.__registerUdevCallback()

    def __registerUdevCallback(self):
        context = pyudev.Context()
        monitor = Monitor.from_netlink(context)
        monitor.filter_by(subsystem='block')
        observer = MonitorObserver(monitor, callback=self.__checkUdevEvent, name='monitor-observer')
        observer.start()

    def __checkUdevEvent(self, device: dict):
        if DISK_EJECT_REQUEST_UDEV_TAG in device:
            self._makeUnavailable()
        elif MEDIA_TRACK_COUNT_AUDIO_UDEV_TAG in device:
            self._makeAvailable()

    def _getRootNodeItem(self) -> NodeItem:
        return self._getNodeItemForPath(self._getPath(self._tree.root))

    def _getParentPath(self, path: Node) -> Node:
        return self._tree.parent(path.identifier)

    def _isLeaf(self, path: Node) -> bool:
        return path.is_leaf()

    def _isPlayable(self, path: Node) -> bool:
        # both RootItem (whole CD) and TrackItem
        return True

    def _getOrderedChildPaths(self, path: Node) -> List[Node]:
        return self._tree.children(path.identifier)

    def _getRootPath(self) -> Node:
        return self._getPath(self._tree.root)

    def _getID(self, path: Node) -> NodeID:
        return path.identifier

    def _getPath(self, nodeID: NodeID) -> Optional[Node]:
        return self._tree.get_node(nodeID)

    def _getNodeLabelFor(self, path: Node) -> str:
        label = path.data.name
        # adding length for tracks
        if isinstance(path.data, TrackItem):
            label += " (" + secsToTime(path.data.lengthSecs) + ")"
        # UNICODE -> ASCII
        return unidecode(label)

    def _getTrackLabelFor(self, path: Node) -> str:
        # UNICODE -> ASCII
        return unidecode(path.data.name)

    def _playNode(self, nodeID: NodeID) -> None:
        node = self._getPath(nodeID)
        if isinstance(node.data, RootItem):
            # whole CD - from track 1
            self.__playFromTrack(1)
        elif isinstance(node.data, TrackItem):
            item = node.data  # type: TrackItem
            trackID = item.trackID
            self.__playFromTrack(trackID)

    def __getTracksCount(self) -> int:
        return len(self._tree.children(self._tree.root))

    def _getPathFor(self, mpvPath: str) -> Optional[Node]:
        """
        CD playback carries information in the path (cdda://), all is controlled by chapters <-> tracks
        :return: Always None, since None disables further processing
        """
        return None

    def _areEqual(self, path1: Node, path2: Node) -> bool:
        return path1.identifier == path2.identifier

    def _getMetadataParserRules(self) -> Dict[Metadata, List[str]]:
        return {}

    def _initValuesForAvailable(self) -> bool:
        tree = CDPlaylist().loadTreeFromCD()
        if tree:
            self._tree = tree
            return super()._initValuesForAvailable()
        else:
            return False

    def _initValuesForUnavailable(self):
        self._tree = None  # type: Tree
        super()._initValuesForUnavailable()

    @staticmethod
    def __isCDInserted() -> bool:
        # using another udev context - running in a different thread
        # noinspection PyBroadException
        try:
            context = pyudev.Context()
            device = Devices.from_device_file(context, DEV_CDROM)
            return MEDIA_TRACK_COUNT_AUDIO_UDEV_TAG in device
        except Exception:
            return False

    def _checkAvailability(self) -> bool:
        return self.__isCDInserted()

    def __playFromTrack(self, trackID: int) -> None:
        # chapters are zero-based
        chapter = trackID - 1
        try:
            self._getMPV().get_property("chapter")
            logging.debug("Chapter property available, just switching")
            self._startPlayback(chapter=chapter)
        except MPVCommandError:
            logging.debug("Chapter property NOT available, loading path and switching to chapter in callback")
            self._startPlayback(mpvPath=CDDA__MPV_FILEPATH)
            self.__chapterToSwitch = chapter

    def chapterWasChanged(self, chapter: Optional[int]) -> None:
        """
        CD playback is controlled by chapters
        """
        if chapter is not None:
            if self.__chapterToSwitch is not None:
                self.__playChapterToSwitch()
            elif chapter >= 0:
                # chapters are 0 ... maxTracks - 1
                childNodes = self._tree.children(self._tree.root)  # type: List[Node]
                if chapter < len(childNodes):
                    newNode = childNodes[chapter]
                    self._switchedToNewPath(newNode)

    def __playChapterToSwitch(self):
        self._startPlayback(chapter=self.__chapterToSwitch)
        self.__chapterToSwitch = None  # type: Optional[int]

    def _convertTimePos(self, timePosFromStart: int) -> Optional[int]:
        """
        CD playback shows time position of currently played track
        """
        node = self._getPlayedNode()
        if node is not None and isinstance(node.data, TrackItem):
            timePos = timePosFromStart - node.data.startsAtSecs
            # always showing the current second, i.e. + 1
            if timePos < 0:
                timePos = 1
            else:
                timePos += 1
            return timePos
        else:
            return None

    def _getDuration(self) -> Optional[int]:
        """
        CD playback shows duration of currently played track
        """
        node = self._getPlayedNode()
        if node is not None and isinstance(node.data, TrackItem):
            return node.data.lengthSecs
        else:
            return None
