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
        self._status = PlaybackStatus.STOPPED
        super().__init__(id=ModuleID.ANALOG_SOURCE, name='AnalogSource', dispatcher=dispatcher)

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

    def _determinePlaybackStatus(self) -> PlaybackStatus:
        return self._status

    def _changePlaybackStatusTo(self, newStatus: PlaybackStatus):
        # TODO - should call the soundcard/hardware mute switch
        self._status = newStatus
