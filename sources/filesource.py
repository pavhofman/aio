from typing import TYPE_CHECKING

from moduleid import ModuleID
from sources.source import Source
from sourcestatus import SourceStatus

if TYPE_CHECKING:
    from dispatcher import Dispatcher


class FileSource(Source):
    def __init__(self, dispatcher: 'Dispatcher'):
        super().__init__(id=ModuleID.FILE_SOURCE, dispatcher=dispatcher)

    def _activate(self) -> bool:
        # no track selected, stopped
        self.status = SourceStatus.STOPPED
        return True
