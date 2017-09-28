from typing import TYPE_CHECKING

from moduleid import ModuleID
from uis.timesourcepart import TimeSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class CDSourcePart(TimeSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(sourceID=ModuleID.CD_SOURCE, name="CD", app=app)
