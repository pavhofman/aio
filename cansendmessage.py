from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dispatcher import Dispatcher
    from moduleid import ModuleID

"""
Mixin holding parameters necessary for sending messages
"""
class CanSendMessage:
    def __init__(self, id: 'ModuleID', dispatcher: 'Dispatcher'):
        self.id = id
        self.dispatcher = dispatcher
