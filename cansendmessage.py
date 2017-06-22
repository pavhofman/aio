from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dispatcher import Dispatcher
    from moduleid import ModuleID


class CanSendMessage:
    def __init__(self, id: 'ModuleID', dispatcher: 'Dispatcher'):
        self.dispatcher = dispatcher
        self.id = id
