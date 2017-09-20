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


"""
Generator of NodeID sequence. Separate instance for each TreeSource  
"""
class NodeIDProvider:
    def __init__(self):
        self.__myLock = Lock()
        self.__lastNodeID = 0

    def getNextID(self) -> NodeID:
        """
        This method is called from multiple threads, incrementing must be secured with a lock
        """
        with locked(self.__myLock):
            self.__lastNodeID += 1
            return self.__lastNodeID
