from dispatcher import Dispatcher
from moduleid import ModuleID
from sources.source import Source
from sourcestatus import SourceStatus

'''
UI 
'''


class AnalogSource(Source):
    def __init__(self, dispatcher: Dispatcher):
        # call the thread class
        super().__init__(id=ModuleID.ANALOG_SOURCE, dispatcher=dispatcher, initStatus=SourceStatus.NOT_ACTIVE)

    def _activate(self) -> bool:
        self.status = SourceStatus.PLAYING
        return True