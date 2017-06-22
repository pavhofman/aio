import logging
from queue import Queue
from typing import TYPE_CHECKING

from remi import Server

import globalvars
from moduleid import ModuleID
from msgconsumer import MsgConsumer
from msgs.message import Message
from uis.webapp import WebApp

if TYPE_CHECKING:
    from dispatcher import Dispatcher

'''
WEB UI 
'''


class WebUI(MsgConsumer):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: 'Dispatcher'):
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher)
        # to make it available to webapp
        self._appQueue = Queue()
        self._server = self._startServer(WebApp, address='0.0.0.0', start_browser=True)

    def stop(self):
        super().stop()
        self._server.stop()

    def _consume(self, msg: 'Message'):
        """
        forward messages to the app only when running, otherwise drop them
        """
        if globalvars.webAppRunning:
            self._appQueue.put(msg)

    def _startServer(self, mainGuiClass, **kwargs) -> 'Server':
        """This method starts the webserver with a specific App subclass."""
        logging.getLogger('remi').setLevel(level=logging.DEBUG)
        return MyServer(mainGuiClass, start=True, **kwargs, userdata=(self.id, self.dispatcher, self._appQueue))


class MyServer(Server):
    # I do not need the server to keep cycling
    def serve_forever(self):
        pass
