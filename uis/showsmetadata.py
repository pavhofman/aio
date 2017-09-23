import abc
import json
from typing import Dict

from metadata import Metadata
from remi import gui
from uis.canappendwidget import CanAppendWidget


# noinspection PyAbstractClass
class ShowsMetadata(CanAppendWidget, abc.ABC):
    """
    Class appends and updates audio params label
    """

    def __init__(self):
        self._metadataLabel = gui.Label("")
        # TODO - key value
        self.append(self._metadataLabel, "8")

    # noinspection PyUnusedLocal
    def _showMetadata(self, mdJson: str):
        mdDict = json.loads(mdJson)  # type: Dict[str, str]
        lines = []
        for type in Metadata:
            if type.value in mdDict:
                lines.append(self.__getLineForMD(type, mdDict[type.value]))
        self._metadataLabel.set_text(str.join('<br>', lines))

    def __getLineForMD(self, md: Metadata, value: str) -> str:
        if md == Metadata.TITLE:
            return value
        elif md == Metadata.BITRATE:
            return value + "kbps"

    def _clearMetadata(self):
        self._metadataLabel.set_text("")
