from typing import TYPE_CHECKING

from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import BiIntegerMsg
from msgs.message import Message
from msgs.nodemsg import MsgNodeItem, NON_EXISTING_NODE_ID, NodeMsg
from remi import gui
from uis.websourcepart import WebSourcePart

if TYPE_CHECKING:
    from uis.webapp import WebApp


class FileSourcePart(WebSourcePart):
    def __init__(self, app: 'WebApp'):
        super().__init__(id=ModuleID.FILE_SOURCE, name="File", app=app)
        self._rootItem = None  # type: MsgNodeItem
        self._requestRootItem()

    def _requestRootItem(self):
        msg = BiIntegerMsg(value1=NON_EXISTING_NODE_ID, value2=0, fromID=self._app.id, typeID=MsgID.REQ_NODE,
                           forID=ModuleID(self.id))
        self._app.dispatcher.distribute(msg)

    def _fillTrackContainer(self, container: gui.Widget) -> None:
        container.append(gui.Label(text=self.name))

    def _fillSelectorContainer(self, container: gui.Widget) -> None:
        pass

    def handleMsgFromSource(self, msg: Message) -> bool:
        if super().handleMsgFromSource(msg):
            return True
        elif msg.typeID == MsgID.NODE_INFO:
            msg = msg  # type: NodeMsg
            self._updateNodeInfo(msg)
            return True
        else:
            return False

    def _updateNodeInfo(self, msg: NodeMsg):
        node = msg.node  # type: 'MsgNodeItem'
        if msg.parentID == NON_EXISTING_NODE_ID:
            self._rootItem = node
