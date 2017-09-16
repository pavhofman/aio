from multiprocessing import Lock
from pathlib import Path
from typing import TYPE_CHECKING, Optional, List, Dict

from unidecode import unidecode

from moduleid import ModuleID
from msgs.nodemsg import NodeID, NodeItem
from sources.mpvtreesource import MPVTreeSource
from sources.mympv import locked
from sources.nodeidprovider import NodeIDProvider

if TYPE_CHECKING:
    from dispatcher import Dispatcher

ROOT_PATH = Path("/home/pavel/Hudba")
# maximum directory depth for recursive loadfile
MAX_DIR_DEPTH = 20


class FileSource(MPVTreeSource[Path], NodeIDProvider):
    def __init__(self, dispatcher: 'Dispatcher'):
        self._pathsByID = {}  # type: Dict[NodeID, Path]
        self._idsByPathStr = {}  # type: Dict[str, NodeID]
        self._cacheLock = Lock()
        NodeIDProvider.__init__(self)
        MPVTreeSource.__init__(self, ModuleID.FILE_SOURCE, dispatcher, monitorTime=True)

    def _getRootNodeItem(self) -> NodeItem:
        return self._getNodeItemForPath(ROOT_PATH)

    def _isAvailable(self) -> bool:
        # TODO
        return True

    def _getParentPath(self, path: Path) -> Path:
        return path.parent

    def _isLeaf(self, path: Path) -> bool:
        return path.is_file() or all(False for _ in path.iterdir())

    def _isPlayable(self, path: Path) -> bool:
        # files and dirs playable
        return True

    def _getOrderedChildPaths(self, path: Path) -> List[Path]:
        return sorted(path.iterdir(), key=lambda k: str(k).lower())

    def _getRootPath(self):
        return ROOT_PATH

    def _getID(self, path: Path) -> NodeID:
        with locked(self._cacheLock):
            pathStr = str(path)
            if pathStr in self._idsByPathStr:
                return self._idsByPathStr[pathStr]
            else:
                # add to caches, generate new ID
                newNodeID = self._getNextID()
                self._pathsByID[newNodeID] = path
                self._idsByPathStr[pathStr] = newNodeID
                return newNodeID

    def _getPath(self, nodeID: NodeID) -> Optional[Path]:
        if nodeID in self._pathsByID.keys():
            return self._pathsByID[nodeID]
        else:
            return None

    def _getNodeLabelFor(self, path: Path) -> str:
        # UNICODE -> ASCII
        # only basename
        return unidecode(path.name)

    def _getTrackLabelFor(self, path: Path) -> str:
        # fullname incl path from ROOT excl
        fullname = str(path)[len(str(ROOT_PATH)):].lstrip('/')
        # UNICODE -> ASCII
        return unidecode(fullname)

    def _playNode(self, nodeID: NodeID) -> None:
        path = self._getPath(nodeID)
        if path is not None:
            self._loadFilesToMPV(path)

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

    def _getPathFor(self, filePath: str) -> Path:
        return Path(filePath)
