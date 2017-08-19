import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg
from msgs.message import Message
from uis.timenodeselectfsbox import TimeNodeSelectFSBox
from uis.timetrackdetailsbox import TimeTrackDetailsBox
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
        self._trackBox.drawTimePos(timePos=timePos, duration=duration)
        self._selectorBox.trackBox.drawTimePos(timePos=timePos, duration=duration)

    def _createSelectorBox(self) -> TimeNodeSelectFSBox:
        return TimeNodeSelectFSBox(self._app, self)

    def _createTrackBox(self) -> 'TimeTrackDetailsBox':
        return TimeTrackDetailsBox(self._app, self)
