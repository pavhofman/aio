import abc
import logging
from typing import TYPE_CHECKING

from groupid import GroupID
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from sources import playcommand
from sources.playbackstatus import PlaybackStatus
from sources.playcommand import PlayCommand
from sources.sourcestatus import SourceStatus

if TYPE_CHECKING:
    from dispatcher import Dispatcher


class Source(MsgConsumer, abc.ABC):
    """
    Source representation. Only one instance for each source within the network
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher'):
        self._initValuesForUnavailable()
        # status init value
        self._status = SourceStatus.UNAVAILABLE  # type: SourceStatus
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher)

    def _initializeInThread(self):
        super()._initializeInThread()
        # status init value
        if self._checkAvailability():
            self._makeAvailable()

    # consuming the message
    def _consume(self, msg: 'Message') -> bool:
        logging.debug(str(self) + " received msg" + msg.__str__())
        if msg.typeID == MsgID.REQ_SOURCE_STATUS:
            self.__sendSourceStatus()
            return True
        elif msg.typeID == MsgID.SOURCE_PLAY_COMMAND:
            msg = msg  # type: IntegerMsg
            command = playcommand.getCommand(msg.value)
            self._executePlayCommand(command)
            return True
        elif msg.typeID == MsgID.ACTIVATE_SOURCE:
            msg = msg  # type: IntegerMsg
            self._handleActivateMsg(msg)
            return True
        else:
            return False

    def _executePlayCommand(self, command: PlayCommand) -> None:
        curPlaybackStatus = self._determinePlaybackStatus()
        if command.isApplicableFor(curPlaybackStatus):
            self._doExecuteCommand(command)

    def _doExecuteCommand(self, command: PlayCommand) -> None:
        if command == PlayCommand.STOP:
            self._changePlaybackStatusTo(PlaybackStatus.STOPPED)
        elif command == PlayCommand.UNPAUSE:
            self._changePlaybackStatusTo(PlaybackStatus.PLAYING)
        elif command == PlayCommand.PAUSE:
            self._changePlaybackStatusTo(PlaybackStatus.PAUSED)
        elif command == PlayCommand.SF:
            self._skipForward()
        elif command == PlayCommand.SB:
            self._skipBackward()
        elif command == PlayCommand.NEXT:
            self._playNext()
        elif command == PlayCommand.PREV:
            self._playPrev()

    def _handleActivateMsg(self, msg: IntegerMsg):
        if msg.value == self.id.value:
            # activate myself
            if self._status.isAvailable():
                self._activate()
        else:
            # activate some other source, i.e. deactivate myself if active
            if self._status.isActivated():
                self._deactive()

    def _changeSourceStatus(self, newStatus: SourceStatus):
        if self._status != newStatus:
            self._status = newStatus
            # and notification on change
            self.__sendSourceStatus()

    def __sendSourceStatus(self):
        statusValue = self._status.value  # type: int
        msg = IntegerMsg(value=statusValue, fromID=self.id, typeID=MsgID.SOURCE_STATUS_INFO,
                         groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

    @abc.abstractmethod
    def _tryToActivate(self) -> bool:
        pass

    def _activate(self) -> None:
        """
        Activates the source.
        :return: if status changed
        """
        if self._tryToActivate():
            self._changeSourceStatus(SourceStatus.ACTIVATED)
        else:
            self._changeSourceStatus(SourceStatus.NOT_ACTIVATED)

    def _deactive(self) -> None:
        """
        Deactivates the source.
        To be extended in ancestors
        :return: if status changed
        """
        self._changeSourceStatus(SourceStatus.NOT_ACTIVATED)

    def _makeUnavailable(self):
        """
        Make the source unavailable. Called from some resource monitor
        Notifies UIs about new status
        To be extended in ancestors
        """
        self._initValuesForUnavailable()
        self._changeSourceStatus(SourceStatus.UNAVAILABLE)

    def _makeAvailable(self) -> bool:
        """
        Make the source available. Called from some resource monitor
        Notifies UIs about new status
        To be extended in ancestors
        :return whether making available succeeded
        """
        if self._initValuesForAvailable():
            self._changeSourceStatus(SourceStatus.NOT_ACTIVATED)
            return True
        else:
            return False

    def _sendPlaybackInfo(self, newPlayback: PlaybackStatus) -> None:
        msg = IntegerMsg(value=newPlayback.value, fromID=self.id, typeID=MsgID.SOURCE_PLAYBACK_INFO,
                         groupID=GroupID.UI)
        self.dispatcher.distribute(msg)

        pass

    def _initValuesForUnavailable(self):
        """
        for descendants
        """
        pass

    def _initValuesForAvailable(self) -> bool:
        """
        for descendants
        :return whether initialization succeeded
        """
        return True

    def _skipForward(self) -> None:
        """
        not defined for basic source
        """
        pass

    def _skipBackward(self) -> None:
        """
        not defined for basic source
        """
        pass

    def _playNext(self) -> None:
        """
        not defined for basic source
        """
        pass

    def _playPrev(self) -> None:
        """
        not defined for basic source
        """
        pass

    @abc.abstractmethod
    def _determinePlaybackStatus(self) -> PlaybackStatus:
        pass

    @abc.abstractmethod
    def _changePlaybackStatusTo(self, newStatus: PlaybackStatus):
        pass

    @abc.abstractmethod
    def _checkAvailability(self):
        """
        Thorough method to check for availability. Called once at source init and
        then usually by some timed task
        :return: true = available, false = unavailable
        """
        pass
