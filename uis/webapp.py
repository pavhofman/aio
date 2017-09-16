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
from uis.activatesourcefsbox import ActivateSourceFSBox
from uis.analogsourcepart import AnalogSourcePart
from uis.filesourcepart import FileSourcePart
from uis.hassourceparts import HasSourceParts
from uis.mainfsbox import MainFSBox
from uis.radiosourcepart import RadioSourcePart
from uis.timedclose import TimedClose
from uis.volumefsbox import VolumeFSBox

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
            FileSourcePart(self),
            RadioSourcePart(self)
        ]

    # noinspection PyAttributeOutsideInit,PyShadowingBuiltins
    def main(self, id: ModuleID, dispatcher: 'Dispatcher', queue: Queue) -> gui.Widget:
        CanSendMessage.__init__(self, id=id, dispatcher=dispatcher)
        HasSourceParts.__init__(self)
        self._inputQueue = queue

        self._rootBox = self._createRootBox()

        """
        rootBox holds the following fullscreen boxes
        * volumeFSBox - volume setting - returns the the previous box after 1 second of inactivity
        * mainFSBox - default, split view
            * left current playback box 
            * right overviewBox
        * sourceSelFSBox - icons of sources, opens upon clicking on sourcesBox in overviewBox
        * sourceBrowserFSBox - for each source 
        """

        # the margin 0px auto centers the main box
        self.mainFSBox = MainFSBox(self)

        self._currentFSBox = self._prevFSBox = self.mainFSBox
        self.setFSBox(self.mainFSBox)
        self._volFSBox = VolumeFSBox(self)
        self._activateSourceFSBox = ActivateSourceFSBox(self)

        # let know the app is running now
        globalvars.webAppRunning = True

        # returning the root widget
        return self._rootBox

    @staticmethod
    def getWidth() -> int:
        return WIDTH

    @staticmethod
    def getHeight() -> int:
        return HEIGHT

    def setFSBox(self, box: gui.Widget):
        if self._currentFSBox is not None \
                and isinstance(self._currentFSBox, TimedClose):
            self._currentFSBox.closeTimer()
        self._prevFSBox = self._currentFSBox  # type: gui.Widget
        self._currentFSBox = box
        self._rootBox.empty()
        self._rootBox.append(box)
        if isinstance(box, TimedClose):
            box.activateTimer()

    @staticmethod
    def _createRootBox() -> gui.Widget:
        box = gui.Widget(width=WIDTH, height=HEIGHT, margin='0px auto',
                         layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        return box

    def idle(self) -> None:
        if globalvars.stopWebApp:
            self.close()

        msg = self._readMsg()
        if msg is not None:
            logging.debug("Web App received " + msg.__str__())
            self._handleMsg(msg)

    def _readMsg(self) -> Optional[Message]:
        try:
            if hasattr(self, '_inputQueue'):
                msg = self._inputQueue.get_nowait()
                return msg
            else:
                return None
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
        self._volFSBox.setVolume(value)
        self.mainFSBox.setVolume(value)

    def showVolFSBox(self) -> None:
        self.setFSBox(self._volFSBox)

    def showActivateSourceFSBox(self) -> None:
        self.setFSBox(self._activateSourceFSBox)

    def showPrevFSBox(self) -> None:
        self.setFSBox(self._prevFSBox)

    def sendSwitchSourceReq(self, source: 'WebSourcePart', activate: bool) -> None:
        msg = self._createActivationMsg(source, activate)
        self.dispatcher.distribute(msg)

    def _createActivationMsg(self, source: 'WebSourcePart', activate: bool) -> IntegerMsg:
        if activate:
            activationSourceID = source.sourceID.value
        else:
            # deactivate this source = deactivate all sources (only one can be activated at any moment)
            activationSourceID = 0
        return IntegerMsg(value=activationSourceID, fromID=self.id, typeID=MsgID.ACTIVATE_SOURCE,
                          groupID=GroupID.SOURCE)
