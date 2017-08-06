import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message
from msgs.nodemsg import NodeMsg
from msgs.trackmsg import TrackItem
from uis.nodeselectfscontainer import NodeSelectFSContainer
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class TreeSourcePart(WebSourcePart, abc.ABC):
    def __init__(self, sourceID: ModuleID, name: str, app: 'WebApp'):
        WebSourcePart.__init__(self, sourceID=sourceID, name=name, app=app)

    def handleMsgFromSource(self, msg: Message) -> bool:
        if super().handleMsgFromSource(msg):
            return True
        elif msg.typeID == MsgID.NODE_INFO:
            msg = msg  # type: NodeMsg
            self._selectorContainer.drawStruct(msg.nodeStruct)
            return True
        else:
            return False

    def _createSelectorContainer(self) -> NodeSelectFSContainer:
        return NodeSelectFSContainer(self._app, self)

    def _showTrackInSelectorContainer(self, trackItem: TrackItem) -> None:
        self._selectorContainer.drawTrack(trackItem)

    def _showTimeInSelectorContainer(self, timePos: int) -> None:
        self._selectorContainer.drawTimePos(timePos)
