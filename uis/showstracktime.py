import abc

from common.timeutils import secsToTime
from remi import gui
from uis.canappendwidget import CanAppendWidget


class ShowsTrackTime(CanAppendWidget, abc.ABC):
    """
    Shows time position and track duration labels
    """

    def __init__(self, posKey: str):
        # labels are inserted into HBox
        self._box = gui.HBox()
        self.append(self._box, posKey)
        self._timePosLabel = gui.Label(text="")
        self._box.append(self._timePosLabel, "1")
        self._separatorLabel = gui.Label(text="")
        self._box.append(self._separatorLabel, "2")
        self._trackDuration = gui.Label(text="")
        self._box.append(self._trackDuration, "3")

    def drawTimePos(self, timePos: int, duration: int) -> None:
        self._timePosLabel.set_text(secsToTime(timePos))
        self._separatorLabel.set_text("of")
        self._trackDuration.set_text(secsToTime(duration))

    def _clearTrackInfo(self):
        self._timePosLabel.set_text("")
        self._separatorLabel.set_text("")
        self._trackDuration.set_text("")
