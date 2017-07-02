from moduleid import ModuleID
from sourcestatus import SourceStatus


class SourcePart:
    def __init__(self, sourceID: ModuleID):
        self.sourceID = sourceID
        self.status = SourceStatus.UNAVAILABLE

    def isSelected(self):
        return self.status.isActive()

    def setStatus(self, newStatus: SourceStatus):
        self.status = newStatus
