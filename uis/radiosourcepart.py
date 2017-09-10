from typing import TYPE_CHECKING

from moduleid import ModuleID
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class RadioSourcePart(WebSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(sourceID=ModuleID.RADIO_SOURCE, name="Radio", app=app)
