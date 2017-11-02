import logging
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgconsumer import MsgConsumer

if TYPE_CHECKING:
    from dispatcher import Dispatcher
"""
sender - relay of messages between serial ports  
"""


class SerialReciever(MsgConsumer):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, name: str, dispatcher: 'Dispatcher', mySideSenderID: ModuleID):
        super().__init__(id, name='SerialReceiver ' + name, dispatcher=dispatcher)
        self.senderID = mySideSenderID

    # consuming the message
    def _consume(self, msg):
        if msg.forID == self.id:
            logging.warning("Message for receiver??")
        else:
            # just distributing the message
            self.dispatcher.distribute(msg, self.senderID)
