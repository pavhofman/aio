import logging

from dispatcher import Dispatcher
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from serialreciever import SerialReciever

"""
sender - relay of messages between serial ports  
"""


class SerialSender(MsgConsumer):
    """
    dispatcher not used yet
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: Dispatcher, otherSideReceiver: SerialReciever):
        # call the thread class
        super().__init__(id, dispatcher)
        self.receiver = otherSideReceiver

    # consuming the message
    def _consume(self, msg):
        if msg.forID == self.id:
            logging.warning("Message for sender??")
        else:
            self.receiver.submit(msg)
