from typing import TYPE_CHECKING

from msgid import MsgID
from msgs.integermsg import BiIntegerMsg
from msgs.nodemsg import NodeStruct, NodeItem, NON_EXISTING_NODE_ID
from remi import gui

if TYPE_CHECKING:
    from uis.nodesourcepart import NodeSourcePart
    from uis.webapp import WebApp

CONTROLS_WIDTH = 60
CUR_TRACK_HEIGHT = 50

SHOW_CHILDREN_COUNT = 4

# initial empty NodeStruct
EMPTY_NODE_STRUCT = NodeStruct(node=NodeItem(nodeID=NON_EXISTING_NODE_ID, label="", isPlayable=False, isLeaf=True),
                               parentID=NON_EXISTING_NODE_ID, children=[], fromIndex=0, total=0)


class NodeSelectFSContainer(gui.HBox):
    def __init__(self, app: 'WebApp', sourcePart: 'NodeSourcePart'):
        gui.HBox.__init__(self, width=app.getWidth(), height=app.getHeight(), margin='0px auto')
        self._sourcePart = sourcePart
        self._app = app
        leftWidth = app.getWidth() - CONTROLS_WIDTH - 10
        self._structContainer = self._createStructContainer(leftWidth, app.getHeight() - CUR_TRACK_HEIGHT)
        self._controlsContainer = self._createControlsContainer(CONTROLS_WIDTH, app.getHeight() - 10)
        self._curTrackContainer = self._createCurTrackContainer(leftWidth, CUR_TRACK_HEIGHT)
        leftCont = gui.VBox(width=leftWidth, height=app.getHeight(), margin='0px auto')
        leftCont.append(self._structContainer, '1')
        leftCont.append(self._curTrackContainer, '2')
        self.append(leftCont, '1')
        self.append(self._controlsContainer, '2')
        self.drawStruct(EMPTY_NODE_STRUCT)

    def _createStructContainer(self, width: int, height: int) -> gui.Widget:
        container = gui.VBox(width=width, height=height, margin='0px auto')
        self._requestRootButton = self._getRequestRootButton()
        return container

    def _getRequestRootButton(self) -> gui.Button:
        button = gui.Button(text="Request root item")
        button.set_on_click_listener(self._onRequestRootButtonPressed)
        return button

    # noinspection PyUnusedLocal
    def _onRequestRootButtonPressed(self, widget):
        self._sendReqNodeMsg(0)

    def _createControlsContainer(self, width: int, height: int) -> gui.Widget:
        container = gui.VBox(width=width, height=height, margin='0px auto')
        self._homeButton = gui.Button("HOME")
        self._homeButton.set_on_click_listener(self._homeButtonOnClick)
        container.append(self._homeButton)
        self._prevButton = gui.Button("PREV")
        self._prevButton.set_on_click_listener(self._prevButtonOnClick)
        container.append(self._prevButton)
        self._closeButton = gui.Button("CLOSE")
        container.append(self._closeButton)
        self._nextButton = gui.Button("NEXT")
        self._nextButton.set_on_click_listener(self._nextButtonOnClick)
        container.append(self._nextButton)
        self._endButton = gui.Button("END")
        self._endButton.set_on_click_listener(self._endButtonOnClick)

        container.append(self._endButton)
        return container

    # noinspection PyUnusedLocal
    def _homeButtonOnClick(self, widget):
        self._sendReqNodeMsg(0)

    # noinspection PyUnusedLocal
    def _prevButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.fromIndex - SHOW_CHILDREN_COUNT
        if fromIndex < 0:
            fromIndex = 0
        self._sendReqNodeMsg(fromIndex)

    # noinspection PyUnusedLocal
    def _nextButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.fromIndex + SHOW_CHILDREN_COUNT
        lastIndex = self._nodeStruct.total - 1
        if fromIndex > lastIndex:
            fromIndex = lastIndex
        self._sendReqNodeMsg(fromIndex)

    # noinspection PyUnusedLocal
    def _endButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.total - SHOW_CHILDREN_COUNT
        if fromIndex < 0:
            fromIndex = 0
        self._sendReqNodeMsg(fromIndex)

    def _sendReqNodeMsg(self, fromIndex: int) -> None:
        msg = BiIntegerMsg(value1=self._nodeStruct.node.nodeID, value2=fromIndex, fromID=self._app.id,
                           typeID=MsgID.REQ_NODE,
                           forID=self._sourcePart.sourceID)
        self._app.dispatcher.distribute(msg)

    def _createCurTrackContainer(self, width: int, height: int) -> gui.Widget:
        return gui.HBox(width=width, height=height, margin='0px auto')

    def drawStruct(self, nodeStruct: NodeStruct) -> None:
        self._updateRequestRootButton(nodeStruct)
        self._nodeStruct = nodeStruct
        self._fillStructContainer()
        self._updateControls()

    def _updateRequestRootButton(self, nodeStruct: NodeStruct) -> None:
        if nodeStruct == EMPTY_NODE_STRUCT:
            # some info has arrived, no need to show the request button
            self._structContainer.append(self._requestRootButton)
        else:
            self._structContainer.remove_child(self._requestRootButton)

    def _updateControls(self) -> None:
        notAtBegin = self._nodeStruct.fromIndex > 0
        self._homeButton.set_enabled(notAtBegin)
        self._prevButton.set_enabled(notAtBegin)

        notAtEnd = self._nodeStruct.total > (self._nodeStruct.fromIndex + SHOW_CHILDREN_COUNT)
        self._nextButton.set_enabled(notAtEnd)
        self._endButton.set_enabled(notAtEnd)

    def _fillStructContainer(self) -> None:
        # todo
        pass
