from enum import Enum


class SourceStatus(Enum):
    UNAVAILABLE = 0
    NOT_SELECTED = 1
    PLAYING = 2
    PAUSED = 3
    STOPPED = 4

    def isSelected(self) -> bool:
        return self.value > SourceStatus.NOT_SELECTED.value

    def isAvailable(self) -> bool:
        return self.value > SourceStatus.UNAVAILABLE.value
