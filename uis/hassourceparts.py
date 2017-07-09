import abc
from typing import DefaultDict, List, Optional

from moduleid import ModuleID
from uis.sourcepart import SourcePart

'''
UI 
'''


class HasSourceParts(abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self):
        # call the thread class
        self.sourceParts = self._initSourceParts()  # type: List['SourcePart']
        self.sourcePartsByID = self._convertToMap(self.sourceParts)
        self.activeSourcePart = None  # type: SourcePart

    @staticmethod
    def _convertToMap(sourceParts: List[SourcePart]) -> DefaultDict[ModuleID, SourcePart]:
        sourcesByID = {}
        for sourcePart in sourceParts:
            sourcesByID[sourcePart.sourceID] = sourcePart
        return sourcesByID

    def getSourcePart(self, modID: ModuleID) -> 'SourcePart':
        return self.sourcePartsByID.get(modID)

    def _getSourcePartFor(self, msg) -> 'SourcePart':
        sourceID = msg.fromID
        # converting to enum object
        modID = ModuleID(sourceID)
        source = self.getSourcePart(modID)
        return source

    def getActiveSource(self) -> Optional[SourcePart]:
        for source in self.sourceParts:
            if source.status.isActivated():
                return source
        return None

    @abc.abstractmethod
    def _initSourceParts(self) -> List['SourcePart']:
        pass
