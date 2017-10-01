from typing import TYPE_CHECKING

from uis.showstracktime import ShowsTrackTime
from uis.simpletrackbox import SimpleTrackBox

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart


class SimpleTimeTrackBox(SimpleTrackBox, ShowsTrackTime):
    def __init__(self, width: int, height: int, sourcePart: 'WebSourcePart'):
        SimpleTrackBox.__init__(self, width=width, height=height, sourcePart=sourcePart)
        ShowsTrackTime.__init__(self, "2")

    def _clearTrackInfo(self):
        SimpleTrackBox._clearTrackInfo(self)
        ShowsTrackTime._clearTrackInfo(self)
