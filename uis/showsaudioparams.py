import abc

from msgs.audioparamsmsg import ParamsItem
from remi import gui
from uis.canappendwidget import CanAppendWidget


# noinspection PyAbstractClass
class ShowsAudioParams(CanAppendWidget, abc.ABC):
    """
    Class appends and updates audio params label
    """

    def __init__(self):
        self._paramsLabel = gui.Label("")
        # TODO - key value
        self.append(self._paramsLabel, "9")

    # noinspection PyUnusedLocal
    def _showParams(self, params: ParamsItem):
        formatStr = str(params.rate) + "/" + str(params.bits) + " , " + str(params.channels) + "ch"
        self._paramsLabel.set_text(formatStr)

    def _clearParams(self):
        self._paramsLabel.set_text("")
