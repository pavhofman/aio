from enum import Enum


class SourceStatus(Enum):
    UNAVAILABLE = 0
    NOT_ACTIVATED = 1
    ACTIVATED = 2

    def isActivated(self) -> bool:
        return self == SourceStatus.ACTIVATED

    def isAvailable(self) -> bool:
        return self.value > SourceStatus.UNAVAILABLE.value
