import logging

from moduleid import ModuleID
from sources.sourcestatus import SourceStatus


class SourcePart:
    def __init__(self, sourceID: ModuleID):
        self.sourceID = sourceID
        self.sourceStatus = SourceStatus.UNAVAILABLE

    def setStatus(self, newStatus: SourceStatus) -> bool:
        if newStatus != self.sourceStatus:
            oldStatus = self.sourceStatus
            self.sourceStatus = newStatus
            logging.debug(str(self) + ": changed status from " + str(oldStatus))
            return True
        else:
            return False

    def __str__(self) -> str:
        return super().__str__() \
               + "; sourceID: " + str(self.sourceID) \
               + "; sourceStatus: " + str(self.sourceStatus)
