import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg
from msgs.message import Message
from uis.timednodeselectfscontainer import TimedNodeSelectFSContainer
from uis.timedtrackcontainer import TimedTrackContainer
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class TimedSourcePart(WebSourcePart, abc.ABC):
    def __init__(self, sourceID: ModuleID, name: str, app: 'WebApp'):
        WebSourcePart.__init__(self, sourceID=sourceID, name=name, app=app)

    def handleMsgFromSource(self, msg: Message) -> bool:
        if super().handleMsgFromSource(msg):
            return True
        elif msg.typeID == MsgID.TIME_POS_INFO:
            msg = msg  # type: BiIntegerMsg
            self._drawTimePos(timePos=msg.value2)
            return True
        else:
            return False

    def _drawTimePos(self, timePos: int) -> None:
        self._trackContainer.drawTimePos(timePos)
        self._selectorContainer.drawTimePos(timePos)

    def _createSelectorContainer(self) -> TimedNodeSelectFSContainer:
        return TimedNodeSelectFSContainer(self._app, self)

    def _createTrackContainer(self) -> 'TimedTrackContainer':
        return TimedTrackContainer(self._app, self)
