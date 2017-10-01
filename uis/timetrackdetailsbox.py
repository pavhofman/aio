from typing import TYPE_CHECKING

from uis.showstracktime import ShowsTrackTime
from uis.trackdetailsbox import TrackDetailsBox

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


class TimeTrackDetailsBox(TrackDetailsBox, ShowsTrackTime):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        # always shows skipping buttons
        TrackDetailsBox.__init__(self, app, sourcePart, showSkipBtns=True)
        ShowsTrackTime.__init__(self)

    def _clearTrackInfo(self):
        TrackDetailsBox._clearTrackInfo(self)
        ShowsTrackTime._clearTrackInfo(self)
