import abc

from common.timeutils import secsToTime
from remi import gui
from uis.canappendwidget import CanAppendWidget


class ShowsTrackTime(CanAppendWidget, abc.ABC):
    """
    Shows time position and track duration labels
    """

    def __init__(self):
        self._timePosLabel = gui.Label(text="")
        self.append(self._timePosLabel, "2")
        self._trackDuration = gui.Label(text="")
        self.append(self._trackDuration, "3")

    def drawTimePos(self, timePos: int, duration: int) -> None:
        self._timePosLabel.set_text(secsToTime(timePos))
        self._trackDuration.set_text(secsToTime(duration))

    def _clearTrackInfo(self):
        self._timePosLabel.set_text("")
        self._trackDuration.set_text("")
