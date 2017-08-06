from moduleid import ModuleID
from sources.sourcestatus import SourceStatus


class SourcePart:
    def __init__(self, sourceID: ModuleID):
        self.sourceID = sourceID
        self.sourceStatus = SourceStatus.UNAVAILABLE

    def setStatus(self, newStatus: SourceStatus):
        self.sourceStatus = newStatus
