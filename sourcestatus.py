from enum import Enum


class SourceStatus(Enum):
    UNAVAILABLE = 0
    NOT_ACTIVE = 1
    PLAYING = 2
    PAUSED = 3
    STOPPED = 4

    def isActive(self) -> bool:
        return self.value > SourceStatus.NOT_ACTIVE.value

    def isAvailable(self) -> bool:
        return self.value > SourceStatus.UNAVAILABLE.value
