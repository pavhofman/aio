from moduleid import ModuleID
from sourcestatus import SourceStatus


class SourceUIPart:
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID):
        self.id = id
        self.status = SourceStatus.UNAVAILABLE

    def isSelected(self):
        return self.status.isActive()

    def setStatus(self, newStatus: SourceStatus):
        self.status = newStatus
