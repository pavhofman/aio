from contextlib import contextmanager
from threading import Lock

from msgs.nodemsg import NodeID


@contextmanager
def locked(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


class NodeIDProvider:
    def __init__(self):
        self.__myLock = Lock()
        self.__lastNodeID = 0

    def _getNextID(self) -> NodeID:
        with locked(self.__myLock):
            self.__lastNodeID += 1
            return self.__lastNodeID
