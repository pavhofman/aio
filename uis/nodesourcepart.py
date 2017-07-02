import abc
from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg
from msgs.message import Message
from msgs.nodemsg import NON_EXISTING_NODE_ID, NodeMsg, NodeStruct
from remi import gui
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class NodeSourcePart(WebSourcePart, abc.ABC):
    # noinspection PyShadowingBuiltins
    def __init__(self, sourceID: ModuleID, name: str, app: 'WebApp'):
        # these params are used in _fillSelectorContainer called from WebSourcePart
        # UGLY!!!
        self._nodeStruct = None  # type: NodeStruct
        self._requestRootButton = self._getRequestRootButton()
        WebSourcePart.__init__(self, sourceID=sourceID, name=name, app=app)
        self._requestRootItem()

    def _requestRootItem(self):
        msg = BiIntegerMsg(value1=NON_EXISTING_NODE_ID, value2=0, fromID=self._app.id, typeID=MsgID.REQ_NODE,
                           forID=ModuleID(self.sourceID))
        self._app.dispatcher.distribute(msg)

    def handleMsgFromSource(self, msg: Message) -> bool:
        if super().handleMsgFromSource(msg):
            return True
        elif msg.typeID == MsgID.NODE_INFO:
            msg = msg  # type: NodeMsg
            self._updateNodeStruct(msg)
            return True
        else:
            return False

    def _updateNodeStruct(self, msg: NodeMsg):
        # some info has arrived, no need to show the request button
        self._selectorContainer.remove_child(self._requestRootButton)
        if self._nodeStruct is None:
            self._nodeStruct = msg.nodeStruct  # type: NodeStruct

    def _fillSelectorContainer(self, container: gui.Widget) -> None:
        if self._nodeStruct is None:
            container.append(self._requestRootButton)

    def _getRequestRootButton(self) -> gui.Button:
        button = gui.Button(text="Request root item")
        button.set_on_click_listener(self._onRequestRootButtonPressed)
        return button

    # noinspection PyUnusedLocal
    def _onRequestRootButtonPressed(self, widget):
        self._requestRootItem()
