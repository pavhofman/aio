import abc
import logging
from queue import Queue
from threading import Thread, Event
from typing import TYPE_CHECKING

from cansendmessage import CanSendMessage
from moduleid import ModuleID
from msgs.message import Message

if TYPE_CHECKING:
    from dispatcher import Dispatcher

"""
Abstract message consumer 
"""


class MsgConsumer(CanSendMessage, Thread, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher'):
        CanSendMessage.__init__(self, id, dispatcher)
        # call the thread class
        Thread.__init__(self)
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
        try:
            while not self.stopped():
                # no timeout
                try:
                    # timeout allows to stop the thread
                    msg = self.receiveQ.get(timeout=3)
                    if msg is not None:
                        self._consume(msg)
                except Exception:
                    # dropping the msg or ignoring the Empty exception, continuing
                    pass
        except Exception as e:
            logging.error(e, exc_info=True)

    def receive(self, msg: 'Message'):
        self.receiveQ.put(msg)

    # consuming the message
    @abc.abstractmethod
    def _consume(self, msg):
        pass

    def close(self):
        self.stop()
