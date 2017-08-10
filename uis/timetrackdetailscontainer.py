from typing import TYPE_CHECKING

from uis.showstracktime import ShowsTrackTime
from uis.trackdetailscontainer import TrackDetailsContainer

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TimeTrackDetailsContainer(TrackDetailsContainer, ShowsTrackTime):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        TrackDetailsContainer.__init__(self, app, sourcePart)
        ShowsTrackTime.__init__(self)

    def _clearTrackInfo(self):
        TrackDetailsContainer._clearTrackInfo(self)
        ShowsTrackTime._clearTrackInfo(self)
