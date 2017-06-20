import abc
import logging
from typing import DefaultDict, List

from dispatcher import Dispatcher
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from sourcestatus import SourceStatus
from uis.sourceuipart import SourceUIPart

'''
UI 
'''


class UI(MsgConsumer, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: Dispatcher):
        # call the thread class
        MsgConsumer.__init__(self, id=id, dispatcher=dispatcher)
        self._volume = 0
        self.sources = self._initSourceParts()
        self.sourcesByID = self._convertToMap(self.sources)
        self.activeSource = None

    @staticmethod
    def _convertToMap(sources: List['SourceUIPart']) -> DefaultDict[ModuleID, SourceUIPart]:
        sourcesByID = {}
        for source in sources:
            sourcesByID[source.id] = source
        return sourcesByID

    def _getUISource(self, modID: ModuleID) -> 'SourceUIPart':
        return self.sourcesByID.get(modID)

    def stop(self):
        super().stop()

    def _getUISourceFor(self, msg) -> 'SourceUIPart':
        sourceID = msg.fromID
        # converting to enum object
        modID = ModuleID(sourceID)
        source = self._getUISource(modID)
        return source

    # consuming the message

    def _consume(self, msg: 'Message'):
        if msg.typeID == MsgID.CURRENT_VOL_INFO:
            msg = msg  # type: IntegerMsg
            self._handleVolMsg(msg)
        elif msg.typeID == MsgID.SOURCE_STATUS_INFO:
            msg = msg  # type: IntegerMsg
            self._handleSourceStatusMsg(msg)

    def _handleVolMsg(self, msg: IntegerMsg):
        newVolume = msg.value
        if self._volume != newVolume:
            self._volume = newVolume
            logging.debug("Changed volume to: " + str(self._volume))

    def close(self):
        super().close()

    def _handleSourceStatusMsg(self, msg: IntegerMsg):
        source = self._getUISourceFor(msg)
        if source is not None:
            newStatus = SourceStatus(msg.value)
            if newStatus != source.status:
                source.status = newStatus
                if newStatus.isActive():
                    self.activeSource = source
                logging.debug("Changed status of UI Source " + source.__class__.__name__ + " to " + str(source.status))

    @abc.abstractmethod
    def _initSourceParts(self) -> List['SourceUIPart']:
        pass
