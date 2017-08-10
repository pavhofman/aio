import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg
from msgs.message import Message
from uis.timenodeselectfscontainer import TimeNodeSelectFSContainer
from uis.timetrackdetailscontainer import TimeTrackDetailsContainer
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class TimeSourcePart(WebSourcePart, abc.ABC):
    """
    Source part supporting TIM_POS_INFO messages, i.e. displaying sources with time position.
    """

    def __init__(self, sourceID: ModuleID, name: str, app: 'WebApp'):
        WebSourcePart.__init__(self, sourceID=sourceID, name=name, app=app)

    def handleMsgFromSource(self, msg: Message) -> bool:
        if super().handleMsgFromSource(msg):
            return True
        elif msg.typeID == MsgID.TIME_POS_INFO:
            msg = msg  # type: BiIntegerMsg
            self._drawTimePos(timePos=msg.value1, duration=msg.value2)
            return True
        else:
            return False

    def _drawTimePos(self, timePos: int, duration: int) -> None:
        self._trackContainer.drawTimePos(timePos=timePos, duration=duration)
        self._selectorContainer.trackBox.drawTimePos(timePos=timePos, duration=duration)

    def _createSelectorContainer(self) -> TimeNodeSelectFSContainer:
        return TimeNodeSelectFSContainer(self._app, self)

    def _createTrackContainer(self) -> 'TimeTrackDetailsContainer':
        return TimeTrackDetailsContainer(self._app, self)
