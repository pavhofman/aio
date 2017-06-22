import logging
from queue import Empty, Queue
from typing import Optional, TYPE_CHECKING, List

from remi import App, gui

import globalvars
from cansendmessage import CanSendMessage
from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from sourcestatus import SourceStatus
from uis.activatesourcefscontainer import ActivateSourceFSContainer
from uis.analogsourceuipart import AnalogSourceUIPart
from uis.filesourceuipart import FileSourceUIPart
from uis.hassourceparts import HasSourceParts
from uis.mainfscontainer import MainFSContainer
from uis.timedclose import TimedClose
from uis.volumefscontainer import VolumeFSContainer

if TYPE_CHECKING:
    from dispatcher import Dispatcher
    from uis.websourceuipart import WebSourceUIPart

WIDTH = 480
HEIGHT = 277


class WebApp(App, CanSendMessage, HasSourceParts['WebSourceUIPart']):
    def __init__(self, *args):
        App.__init__(self, *args)

    def _initSourceParts(self) -> List['WebSourceUIPart']:
        return [
            AnalogSourceUIPart(),
            FileSourceUIPart()
        ]

    # noinspection PyAttributeOutsideInit,PyShadowingBuiltins
    def main(self, id: ModuleID, dispatcher: 'Dispatcher', queue: Queue) -> gui.Widget:
        # let know the app is running now
        globalvars.webAppRunning = True
        CanSendMessage.__init__(self, id=id, dispatcher=dispatcher)
        HasSourceParts.__init__(self)
        self._inputQueue = queue

        self._initSources()
        self._rootContainer = self._createRootContainer()

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
        self._activateSourceFSContainer = ActivateSourceFSContainer(self)

        # returning the root widget
        return self._rootContainer

    # noinspection PyAttributeOutsideInit
    def _initSources(self) -> None:
        for source in self.sourceParts:  # type: WebSourceUIPart
            source.appIsRunning(self)

    @staticmethod
    def getWidth() -> int:
        return WIDTH

    @staticmethod
    def getHeight() -> int:
        return HEIGHT

    def _setFSContainer(self, container: gui.Widget):
        self._prevFSContainer = self._currentFSContainer
        self._currentFSContainer = container
        self._rootContainer.empty()
        self._rootContainer.append(container)
        if isinstance(container, TimedClose):
            container.activateTimer()

    @staticmethod
    def _createRootContainer() -> gui.Widget:
        container = gui.Widget(width=WIDTH, height=HEIGHT, margin='0px auto',
                               layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        container.style['display'] = 'block'
        container.style['overflow'] = 'hidden'
        return container

    def idle(self) -> None:
        msg = self._readMsg()
        if msg is not None:
            logging.debug("Web App received " + msg.toString())
            self._handleMsg(msg)

    def _readMsg(self) -> Optional[Message]:
        try:
            msg = self._inputQueue.get_nowait()
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

    def setVolume(self, value: int) -> None:
        self._volFSContainer.setVolume(value)
        self._mainFSContainer.setVolume(value)

    def showVolFSContainer(self) -> None:
        self._setFSContainer(self._volFSContainer)

    def showActivateSourceFSContainer(self) -> None:
        self._setFSContainer(self._activateSourceFSContainer)

    def showPrevFSContainer(self) -> None:
        if isinstance(self._currentFSContainer, TimedClose):
            self._currentFSContainer.closeTimer()
        self._setFSContainer(self._prevFSContainer)

    def _setSourceStatus(self, sourceID: ModuleID, statusID: int):
        source = self.getSourcePart(sourceID)
        status = SourceStatus(statusID)
        # update source
        source.setStatus(status)
        # update trackcontainer
        if status.isActive():
            self._mainFSContainer.setTrackContainer(source.getTrackContainer())

        elif self.getActiveSource() is None:
            # deactivated
            self._mainFSContainer.setNoTrackContainer()

    def sendSwitchSourceReq(self, source: 'WebSourceUIPart', activate: bool) -> None:
        msg = self._createActivationMsg(source, activate)
        self.dispatcher.distribute(msg)

    def _createActivationMsg(self, source: 'WebSourceUIPart', activate: bool) -> IntegerMsg:
        if activate:
            return IntegerMsg(value=source.id.value, fromID=self.id, typeID=MsgID.ACTIVATE_SOURCE,
                              groupID=GroupID.SOURCE)
        else:
            # deactivate this specific source
            return IntegerMsg(value=SourceStatus.NOT_ACTIVE.value, fromID=self.id, typeID=MsgID.SET_SOURCE_STATUS,
                              forID=source.id)
