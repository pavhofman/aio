from typing import TYPE_CHECKING

from moduleid import ModuleID
from uis.trackdetailsbox import TrackDetailsBox
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class RadioSourcePart(WebSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(sourceID=ModuleID.RADIO_SOURCE, name="Radio", app=app)

    def _createTrackBox(self) -> 'TrackDetailsBox':
        # no skip buttons (no timing), but next/prev is available
        return TrackDetailsBox(self._app, self, showSkipBtns=False, showNextBtns=True)
