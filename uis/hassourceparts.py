import abc
from typing import DefaultDict, List, TypeVar, Generic, Optional

from moduleid import ModuleID

'''
UI 
'''
SOURCE_PART = TypeVar('SOURCE_PART')


class HasSourceParts(Generic[SOURCE_PART], abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self):
        # call the thread class
        self.sourceParts = self._initSourceParts()  # type: List['SOURCE_PART']
        self.sourcePartsByID = self._convertToMap(self.sourceParts)
        self.activeSourcePart = None  # type: SOURCE_PART

    @staticmethod
    def _convertToMap(sources: List[SOURCE_PART]) -> DefaultDict[ModuleID, SOURCE_PART]:
        sourcesByID = {}
        for source in sources:
            sourcesByID[source.id] = source
        return sourcesByID

    def getSourcePart(self, modID: ModuleID) -> 'SOURCE_PART':
        return self.sourcePartsByID.get(modID)

    def _getSourcePartFor(self, msg) -> 'SOURCE_PART':
        sourceID = msg.fromID
        # converting to enum object
        modID = ModuleID(sourceID)
        source = self.getSourcePart(modID)
        return source

    def getActiveSource(self) -> Optional[SOURCE_PART]:
        for source in self.sourceParts:
            if source.status.isActive():
                return source
        return None

    @abc.abstractmethod
    def _initSourceParts(self) -> List['SOURCE_PART']:
        pass
