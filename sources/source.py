import abc
import logging
from typing import TYPE_CHECKING

from groupid import GroupID
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from sources.playbackstatus import PlaybackStatus
from sourcestatus import SourceStatus

if TYPE_CHECKING:
    from dispatcher import Dispatcher


class Source(MsgConsumer, abc.ABC):
    """
    Source representation. Only one instance for each source within the network
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher'):
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher)
        # status init value
        self._status = SourceStatus.NOT_ACTIVATED if self._isAvailable() \
            else SourceStatus.UNAVAILABLE  # type: SourceStatus

    # consuming the message
    def _consume(self, msg: 'Message') -> bool:
        logging.debug(str(self) + " received msg" + msg.__str__())
        if msg.typeID == MsgID.REQ_SOURCE_STATUS:
            self.__sendSourceStatus()
            return True
        elif msg.typeID == MsgID.SET_SOURCE_PLAYBACK:
            msg = msg  # type: IntegerMsg
            newPlayback = PlaybackStatus(msg.value)
            self._setPlayback(newPlayback)
            return True
        elif msg.typeID == MsgID.ACTIVATE_SOURCE:
            msg = msg  # type: IntegerMsg
            self._handleActivateMsg(msg)
            return True
        else:
            return False

    def _setPlayback(self, newPlayback: PlaybackStatus):
        currentPlayback = self._determinePlayback()
        if currentPlayback != newPlayback:
            # changing
            if self._changePlaybackTo(newPlayback):
                # informing
                self._sendPlaybackInfo(newPlayback)

    def _handleActivateMsg(self, msg: IntegerMsg):
        if msg.value == self.id.value:
            # activate myself
            if self._status.isAvailable():
                if self._activate():
                    self.__sendSourceStatus()
        else:
            # activate some other source, i.e. deactivate myself if active
            if self._status.isActivated():
                if self._deactive():
                    self.__sendSourceStatus()

    def __sendSourceStatus(self):
        statusValue = self._status.value  # type: int
        msg = IntegerMsg(value=statusValue, fromID=self.id, typeID=MsgID.SOURCE_STATUS_INFO,
                         groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    @abc.abstractmethod
    def _tryToActivate(self) -> bool:
        pass

    def _activate(self) -> bool:
        """
        Activates the source.
        :return: if status changed
        """
        if self._tryToActivate():
            self._status = SourceStatus.ACTIVATED
            return True
        else:
            self._status = SourceStatus.NOT_ACTIVATED
            return False

    def _deactive(self) -> bool:
        """
        Deactivates the source.
        To be extended in ancestors
        :return: if status changed
        """
        self._status = SourceStatus.NOT_ACTIVATED
        return True

    @abc.abstractmethod
    def _isAvailable(self) -> bool:
        pass

    def _sendPlaybackInfo(self, newPlayback: PlaybackStatus) -> None:
        msg = IntegerMsg(value=newPlayback.value, fromID=self.id, typeID=MsgID.SOURCE_PLAYBACK_INFO,
                         groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

        pass

    @abc.abstractmethod
    def _determinePlayback(self) -> PlaybackStatus:
        pass

    @abc.abstractmethod
    def _changePlaybackTo(self, newPlayback: PlaybackStatus):
        pass
