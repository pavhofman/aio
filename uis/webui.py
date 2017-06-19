import logging
from typing import List

from remi import Server

import globals
from dispatcher import Dispatcher
from moduleid import ModuleID
from msgs.message import Message
from uis.analogsourceuipart import AnalogSourceUIPart
from uis.filesourceuipart import FileSourceUIPart
from uis.ui import UI
from uis.webapp import WebApp
from uis.websourceuipart import WebSourceUIPart

'''
WEB UI 
'''


class WebUI(UI):
    # noinspection PyShadowingBuiltins
    def __init__(self, id: ModuleID, dispatcher: Dispatcher):
        # call the thread class
        super().__init__(id=id, dispatcher=dispatcher)
        # to make it available to webapp
        self._server = self._startServer(WebApp, address='0.0.0.0', start_browser=True)

    def stop(self):
        super().stop()
        self._server.stop()

    def _initSourceParts(self) -> List['WebSourceUIPart']:
        return [
            AnalogSourceUIPart(),
            FileSourceUIPart()
        ]

    def _consume(self, msg: 'Message'):
        """
        forward messages to the app only when running, otherwise drop them
        """
        if globals.webAppRunning:
            globals.webQueue.put(msg)

    # noinspection PyUnusedLocal
    def _startServer(self, mainGuiClass, **kwargs) -> 'Server':
        """This method starts the webserver with a specific App subclass."""
        logging.getLogger('remi').setLevel(level=logging.DEBUG)
        return MyServer(mainGuiClass, start=True, userdata=(self,))


class MyServer(Server):
    # I do not need the server to keep cycling
    def serve_forever(self):
        pass
