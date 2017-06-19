import abc
import logging
from threading import Thread, Event

from msgs.message import Message

'''
Reading messages
Sending to dispatcher queue
In MCU will run in ISR
'''


class AbstractReader(Thread, abc.ABC):
    def __init__(self):
        # call the thread class
        super().__init__()
        self.__event = Event()
        self.setDaemon(True)
        self.start()

    def stop(self):
        self.__event.set()

    def stopped(self) -> bool:
        return self.__event.isSet()

    def run(self):
        try:
            while not self.stopped():
                msg = self._readMsg()
                if msg is not None:
                    self._processMsg(msg)
        except Exception as e:
            logging.error(e, exc_info=True)

    @abc.abstractmethod
    def _readMsg(self) -> 'Message':
        pass

    def close(self):
        self.stop()

    @abc.abstractmethod
    def _processMsg(self, msg):
        pass
