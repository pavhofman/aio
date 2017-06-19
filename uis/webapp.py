import logging
from queue import Empty
from typing import Optional, TYPE_CHECKING, List

from remi import App, gui

import globals
from dispatcher import Dispatcher
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from sourcestatus import SourceStatus
from uis.mainfscontainer import MainFSContainer
from uis.sourceselfscontainer import SourceSelFSContainer
from uis.timedclose import TimedClose
from uis.volumefscontainer import VolumeFSContainer

if TYPE_CHECKING:
    from uis.webui import WebUI
    from uis.websourceuipart import WebSourceUIPart

WIDTH = 480
HEIGHT = 277


class WebApp(App):
    def __init__(self, *args):
        super(WebApp, self).__init__(*args)

    # noinspection PyAttributeOutsideInit
    def main(self, webui: 'WebUI') -> gui.Widget:
        # let know the app is running now
        globals.webAppRunning = True
        self._webui = webui

        self._initSources()
        self._rootContainer = self._getRootContainer()

        """
        rootContainer holds the following fullscreen containers
        * volumeFSContainer - volume setting - returns the the previous container after 1 second of inactivity
        * mainFSContainer - default, split view
            * left current playback container 
            * right overviewContainer
        * sourceSelFSContainer - icons of sources, opens upon clicking on sourcesContainer in overviewContainer
        * sourceBrowserFSContainer - for each source 
        """

        # the margin 0px auto centers the main container
        self._mainFSContainer = MainFSContainer(self)

        self._currentFSContainer = self._prevFSContainer = self._mainFSContainer
        self._setFSContainer(self._mainFSContainer)
        self._volFSContainer = VolumeFSContainer(self)
        self._sourceSelFSContainer = SourceSelFSContainer(self)

        # returning the root widget
        return self._rootContainer

    # delayed initialization after app started
    def _initSources(self):
        for source in self._webui.sources:  # type: WebSourceUIPart
            source.appRunning(self)

    def getDispatcher(self) -> Dispatcher:
        return self._webui.dispatcher

    def getID(self) -> ModuleID:
        return self._webui.id

    @staticmethod
    def getWidth():
        return WIDTH

    @staticmethod
    def getHeight():
        return HEIGHT

    def _setFSContainer(self, container: gui.Widget):
        self._prevFSContainer = self._currentFSContainer
        self._currentFSContainer = container
        self._rootContainer.empty()
        self._rootContainer.append(container)
        if isinstance(container, TimedClose):
            container.activateTimer()

    @staticmethod
    def _getRootContainer() -> gui.Widget:
        container = gui.Widget(width=WIDTH, height=HEIGHT, margin='0px auto',
                               layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        container.style['display'] = 'block'
        container.style['overflow'] = 'hidden'
        return container

    def idle(self):
        msg = self._readMsg()
        if msg is not None:
            logging.debug("Web App received " + msg.toString())
            self._handleMsg(msg)

    @staticmethod
    def _readMsg() -> Optional[Message]:
        try:
            msg = globals.webQueue.get_nowait()
            return msg
        except Empty:
            return None

    def _handleMsg(self, msg: 'Message'):
        if msg.typeID == MsgID.CURRENT_VOL_INFO:
            msg = msg  # type: IntegerMsg
            self.setVolume(msg.value)
        if msg.typeID == MsgID.SOURCE_STATUS_INFO:
            msg = msg  # type: IntegerMsg
            self._handleSetSourceStatusMsg(msg)

    def _handleSetSourceStatusMsg(self, msg: IntegerMsg) -> None:
        self._setSourceStatus(msg.fromID, msg.value)

    def setVolume(self, value: int):
        self._volFSContainer.setVolume(value)
        self._mainFSContainer.setVolume(value)

    def showVolFSContainer(self):
        self._setFSContainer(self._volFSContainer)

    def showSourceSelFSContainer(self):
        self._setFSContainer(self._sourceSelFSContainer)

    def showPrevFSContainer(self):
        self._setFSContainer(self._prevFSContainer)

    def _setSourceStatus(self, sourceID: ModuleID, statusID: int):
        source = self._getSource(sourceID)
        source.setStatus(SourceStatus(statusID))

    def getSources(self) -> List['WebSourceUIPart']:
        return self._webui.sources

    def _getSource(self, sourceID: ModuleID) -> 'WebSourceUIPart':
        return self._webui.sourcesByID[sourceID]
