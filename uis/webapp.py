import logging
from queue import Empty, Queue
from typing import Optional, TYPE_CHECKING, List

import globalvars
from cansendmessage import CanSendMessage
from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from remi import App, gui
from sourcestatus import SourceStatus
from uis.activatesourcefscontainer import ActivateSourceFSContainer
from uis.analogsourcepart import AnalogSourcePart
from uis.filesourcepart import FileSourcePart
from uis.hassourceparts import HasSourceParts
from uis.mainfscontainer import MainFSContainer
from uis.timedclose import TimedClose
from uis.volumefscontainer import VolumeFSContainer

if TYPE_CHECKING:
    from dispatcher import Dispatcher
    from uis.websourcepart import WebSourcePart

WIDTH = 480
HEIGHT = 277


class WebApp(App, CanSendMessage, HasSourceParts):
    def __init__(self, *args):
        App.__init__(self, *args)

    def _initSourceParts(self) -> List['WebSourcePart']:
        return [
            AnalogSourcePart(self),
            FileSourcePart(self)
        ]

    # noinspection PyAttributeOutsideInit,PyShadowingBuiltins
    def main(self, id: ModuleID, dispatcher: 'Dispatcher', queue: Queue) -> gui.Widget:
        # let know the app is running now
        globalvars.webAppRunning = True
        CanSendMessage.__init__(self, id=id, dispatcher=dispatcher)
        HasSourceParts.__init__(self)
        self._inputQueue = queue

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
        self.mainFSContainer = MainFSContainer(self)

        self._currentFSContainer = self._prevFSContainer = self.mainFSContainer
        self.setFSContainer(self.mainFSContainer)
        self._volFSContainer = VolumeFSContainer(self)
        self._activateSourceFSContainer = ActivateSourceFSContainer(self)

        # returning the root widget
        return self._rootContainer

    @staticmethod
    def getWidth() -> int:
        return WIDTH

    @staticmethod
    def getHeight() -> int:
        return HEIGHT

    def setFSContainer(self, container: gui.Widget):
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
        return container

    def idle(self) -> None:
        if globalvars.stopWebApp:
            self.close()

        msg = self._readMsg()
        if msg is not None:
            logging.debug("Web App received " + msg.__str__())
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
        elif msg.fromID in globalvars.realSourceIDs:
            sourcePart = self.getSourcePart(msg.fromID)  # type: WebSourcePart
            sourcePart.handleMsgFromSource(msg)

    def setVolume(self, value: int) -> None:
        self._volFSContainer.setVolume(value)
        self.mainFSContainer.setVolume(value)

    def showVolFSContainer(self) -> None:
        self.setFSContainer(self._volFSContainer)

    def showActivateSourceFSContainer(self) -> None:
        self.setFSContainer(self._activateSourceFSContainer)

    def showPrevFSContainer(self) -> None:
        if isinstance(self._currentFSContainer, TimedClose):
            self._currentFSContainer.closeTimer()
        self.setFSContainer(self._prevFSContainer)

    def sendSwitchSourceReq(self, source: 'WebSourcePart', activate: bool) -> None:
        msg = self._createActivationMsg(source, activate)
        self.dispatcher.distribute(msg)

    def _createActivationMsg(self, source: 'WebSourcePart', activate: bool) -> IntegerMsg:
        if activate:
            return IntegerMsg(value=source.sourceID.value, fromID=self.id, typeID=MsgID.ACTIVATE_SOURCE,
                              groupID=GroupID.SOURCE)
        else:
            # deactivate this specific source
            return IntegerMsg(value=SourceStatus.NOT_ACTIVE.value, fromID=self.id, typeID=MsgID.SET_SOURCE_STATUS,
                              forID=source.sourceID)
