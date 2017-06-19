import abc
import logging
from queue import Queue
from threading import Thread, Event

import dispatcher
from moduleid import ModuleID
from msgs.message import Message

"""
Abstract message consumer 
"""


class MsgConsumer(Thread, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'dispatcher.Dispatcher'):
        # call the thread class
        super().__init__()
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

    def submit(self, msg: 'Message'):
        self.receiveQ.put(msg)

    # consuming the message
    @abc.abstractmethod
    def _consume(self, msg):
        pass

    def close(self):
        self.stop()
