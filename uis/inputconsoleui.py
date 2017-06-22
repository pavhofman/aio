from typing import TYPE_CHECKING

from moduleid import ModuleID
from uis.consoleui import ConsoleUI
from uis.inputreader import InputReader

if TYPE_CHECKING:
    from dispatcher import Dispatcher
'''
UI 
'''


class InputConsoleUI(ConsoleUI):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher'):
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher)
        self._inputreader = InputReader(self.id, self)

    def stop(self):
        super().stop()
        self._inputreader.stop()

    def close(self):
        super().close()
        self._inputreader.close()
