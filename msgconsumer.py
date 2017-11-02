import abc
import logging
from queue import Queue, Empty
from threading import Thread, Event
from typing import TYPE_CHECKING, List

import dispatcher
from cansendmessage import CanSendMessage
from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message

if TYPE_CHECKING:
    from dispatcher import Dispatcher

"""
Abstract message consumer 
"""


class MsgConsumer(CanSendMessage, Thread, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, name: str, dispatcher: 'Dispatcher'):
        CanSendMessage.__init__(self, id, dispatcher)
        # call the thread class
        Thread.__init__(self)
        self.name = name
        self.dispatcher = dispatcher
        self.__event = Event()
        # command queue - contains XXXCommands
        self.receiveQ = Queue()
        self.setDaemon(True)
        # unique ID among modules of same type
        self.id = id
        self.start()

    def stop(self):
        self.__event.set()

    def stopped(self) -> bool:
        return self.__event.isSet()

    def run(self):
        self._initializeInThread()
        try:
            while not self.stopped():
                # no timeout
                try:
                    # timeout allows to stop the thread
                    msg = self.receiveQ.get(timeout=3)
                    if msg is not None:
                        self._consume(msg)
                except Empty:
                    # dropping the msg or ignoring the Empty exception, continuing
                    pass
        except Exception as e:
            logging.error(e, exc_info=True)

    def receive(self, msg: 'Message'):
        self.receiveQ.put(msg)

    # consuming the message
    @abc.abstractmethod
    def _consume(self, msg: 'Message') -> bool:
        """
        Consume the message
        :param msg: Message to consume
        :return: was consumed
        """
        pass

    def close(self):
        self.stop()

    def _initializeInThread(self):
        # always sending "I am here" msg at start, to fill route maps of all dispatchers
        self.dispatcher.distribute(
            IntegerMsg(self._getEncodedGroupIDs(), self.id, MsgID.IN_GROUPS_MSG), self.id)

    def _getEncodedGroupIDs(self) -> int:
        groupIDs = self._getGroupIDs()  # type: List[GroupID]
        return dispatcher.encodeGroupIDs(groupIDs)

    def _getGroupIDs(self) -> List[GroupID]:
        return []

    def __str__(self) -> str:
        return self.name
