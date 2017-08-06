from typing import TYPE_CHECKING

from uis.trackcontainer import TrackContainer

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TimedTrackContainer(TrackContainer):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        TrackContainer.__init__(self, app, sourcePart)

    def drawTimePos(self, timePos: int, duration: int) -> None:
        pass
