from typing import List

from dispatcher import Dispatcher
from moduleid import ModuleID
from msgs.message import Message
from uis.sourceuipart import SourceUIPart
from uis.ui import UI

'''
UI 
'''


class ConsoleUI(UI):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: Dispatcher):
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher)

    # consuming the message
    def _consume(self, msg: 'Message'):
        super()._consume(msg)
        print(self.__class__.__name__ + " received msg: " + msg.toString())

    def _initSourceParts(self) -> List['SourceUIPart']:
        return [
            SourceUIPart(id=ModuleID.ANALOG_SOURCE),
            SourceUIPart(id=ModuleID.FILE_SOURCE)
        ]
