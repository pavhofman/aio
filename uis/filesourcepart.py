from typing import TYPE_CHECKING

from moduleid import ModuleID
from uis.timedsourcepart import TimedSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class FileSourcePart(TimedSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(sourceID=ModuleID.FILE_SOURCE, name="File", app=app)