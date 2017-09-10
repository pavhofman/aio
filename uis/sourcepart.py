from moduleid import ModuleID
from sources.sourcestatus import SourceStatus


class SourcePart:
    def __init__(self, sourceID: ModuleID):
        self.sourceID = sourceID
        self.sourceStatus = SourceStatus.UNAVAILABLE

    def setStatus(self, newStatus: SourceStatus):
        self.sourceStatus = newStatus

    def __str__(self) -> str:
        return super().__str__() \
               + "; sourceID: " + str(self.sourceID) \
               + "; sourceStatus: " + str(self.sourceStatus)
