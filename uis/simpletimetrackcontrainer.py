from typing import TYPE_CHECKING

from uis.showstracktime import ShowsTrackTime
from uis.simpletrackcontainer import SimpleTrackContainer

if TYPE_CHECKING:
    from uis.webapp import WebApp
    from uis.websourcepart import WebSourcePart


class SimpleTimeTrackContainer(SimpleTrackContainer, ShowsTrackTime):
    def __init__(self, width: int, height: int, app: 'WebApp', sourcePart: 'WebSourcePart'):
        SimpleTrackContainer.__init__(self, width=width, height=height, app=app, sourcePart=sourcePart)
        ShowsTrackTime.__init__(self)

    def _clearTrackInfo(self):
        SimpleTrackContainer._clearTrackInfo(self)
        ShowsTrackTime._clearTrackInfo(self)
