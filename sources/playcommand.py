from enum import Enum
from typing import List

from sources.playbackstatus import PlaybackStatus


class PlayCommand(Enum):
    """
    Requested playback command
    """
    STOP = (0, [PlaybackStatus.PLAYING, PlaybackStatus.PAUSED])
    UNPAUSE = (1, [PlaybackStatus.PAUSED])
    PAUSE = (2, [PlaybackStatus.PLAYING])
    # skip forward
    SF = (3, [PlaybackStatus.PLAYING, PlaybackStatus.PAUSED])
    # skip backward
    SB = (4, [PlaybackStatus.PLAYING, PlaybackStatus.PAUSED])
    # next track
    NEXT = (5, [PlaybackStatus.PLAYING, PlaybackStatus.PAUSED])
    # previous track
    PREV = (6, [PlaybackStatus.PLAYING, PlaybackStatus.PAUSED])

    # noinspection PyInitNewSignature
    def __init__(self, id: int, applicableStatuses: List[PlaybackStatus]):
        """

        :param id: ID sent in message
        :param applicableStatuses: For which playback status the play command makes sense
        """
        self.id = id
        self.applicableStatuses = applicableStatuses

    def isApplicableFor(self, status: PlaybackStatus) -> bool:
        return status in self.applicableStatuses


class NotFoundError(Exception):
    pass


def getCommand(id: int) -> PlayCommand:
    for command in PlayCommand:
        if command.id == id:
            return command
    raise NotFoundError("No PlayCommand of id " + str(id))
