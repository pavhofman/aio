from typing import TYPE_CHECKING

from moduleid import ModuleID
from sources.playbackstatus import PlaybackStatus
from sources.source import Source

if TYPE_CHECKING:
    from dispatcher import Dispatcher
'''
UI 
'''


class AnalogSource(Source):
    def __init__(self, dispatcher: 'Dispatcher'):
        # call the thread class
        self._playback = PlaybackStatus.STOPPED
        super().__init__(id=ModuleID.ANALOG_SOURCE, dispatcher=dispatcher)

    def _tryToActivate(self) -> bool:
        # TODO - switch input
        return True

    def _isAvailable(self) -> bool:
        """
        Always available, no need to keep the status in any variable
        """
        return True

    def _checkAvailability(self):
        """
        Always available
        """
        return True

    def _determinePlayback(self) -> PlaybackStatus:
        return self._playback

    def _changePlaybackTo(self, newPlayback: PlaybackStatus):
        # TODO - should call the soundcard/hardware mute switch
        self._playback = newPlayback
