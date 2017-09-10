import abc
from typing import TYPE_CHECKING, Optional

from msgid import MsgID
from msgs.integermsg import BiIntegerMsg, IntegerMsg
from msgs.nodemsg import NodeStruct, NodeItem, NON_EXISTING_NODE_ID, NodeID
from remi import gui
from sources.treesource import MAX_CHILDREN
from uis.simpletrackbox import SimpleTrackBox

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp

CONTROLS_WIDTH = 60
CUR_TRACK_HEIGHT = 50

# initial empty NodeStruct
EMPTY_NODE_ITEM = NodeItem(nodeID=NON_EXISTING_NODE_ID, label="", isPlayable=False, isLeaf=True)
EMPTY_NODE_STRUCT = NodeStruct(node=EMPTY_NODE_ITEM,
                               rootNode=EMPTY_NODE_ITEM, totalParents=0, parentID=NON_EXISTING_NODE_ID,
                               children=[], fromChildIndex=0, totalChildren=0)


class NodeSelectFSBox(gui.HBox):
    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        gui.HBox.__init__(self, width=app.getWidth(), height=app.getHeight(), margin='0px auto')
        self._sourcePart = sourcePart
        self._app = app
        self._leftWidth = app.getWidth() - CONTROLS_WIDTH - 10
        self._structBox = self._createStructBox(self._leftWidth, app.getHeight() - CUR_TRACK_HEIGHT)
        self._controlsBox = self._createControlsBox(CONTROLS_WIDTH, app.getHeight() - 10)
        self.trackBox = self._createTrackBox(self._leftWidth, CUR_TRACK_HEIGHT)
        leftBox = gui.VBox(width=self._leftWidth, height=app.getHeight(), margin='0px auto')
        leftBox.append(self._structBox, '1')
        leftBox.append(self.trackBox, '2')
        self.append(leftBox, '1')
        self.append(self._controlsBox, '2')
        self._nodeStruct = None  # type: Optional[NodeStruct]
        self.drawStruct(EMPTY_NODE_STRUCT)
        # request root node
        self.sendReqNodeMsg(NON_EXISTING_NODE_ID, 0)

    def _createStructBox(self, width: int, height: int) -> gui.Widget:
        box = gui.VBox(width=width, height=height, margin='0px auto')
        self._requestRootButton = self._getRequestRootButton()
        return box

    def _getRequestRootButton(self) -> gui.Button:
        button = gui.Button(text="Request root item")
        button.set_on_click_listener(self._onRequestRootButtonPressed)
        return button

    # noinspection PyUnusedLocal
    def _onRequestRootButtonPressed(self, widget):
        self.sendReqNodeMsg(NON_EXISTING_NODE_ID, 0)

    # noinspection PyUnusedLocal

    def _createControlsBox(self, width: int, height: int) -> gui.Widget:
        box = gui.VBox(width=width, height=height, margin='0px auto')
        self._homeButton = gui.Button("HOME")
        self._homeButton.set_on_click_listener(self._homeButtonOnClick)
        box.append(self._homeButton)
        self._prevButton = gui.Button("PREV")
        self._prevButton.set_on_click_listener(self._prevButtonOnClick)
        box.append(self._prevButton)
        self._closeButton = gui.Button("CLOSE")
        box.append(self._closeButton)
        self._closeButton.set_on_click_listener(self._closeButtonOnClick)
        self._nextButton = gui.Button("NEXT")
        self._nextButton.set_on_click_listener(self._nextButtonOnClick)
        box.append(self._nextButton)
        self._endButton = gui.Button("END")
        self._endButton.set_on_click_listener(self._endButtonOnClick)

        box.append(self._endButton)
        return box

    # noinspection PyUnusedLocal
    def _homeButtonOnClick(self, widget):
        self.sendReqNodeMsg(self._nodeStruct.node.nodeID, 0)

    # noinspection PyUnusedLocal

    def _prevButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.fromChildIndex - MAX_CHILDREN
        if fromIndex < 0:
            fromIndex = 0
        self.sendReqNodeMsg(self._nodeStruct.node.nodeID, fromIndex)

    # noinspection PyUnusedLocal

    def _nextButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.fromChildIndex + MAX_CHILDREN
        lastIndex = self._nodeStruct.totalChildren - 1
        if fromIndex > lastIndex:
            fromIndex = lastIndex
        self.sendReqNodeMsg(self._nodeStruct.node.nodeID, fromIndex)

    # noinspection PyUnusedLocal

    # noinspection PyUnusedLocal
    def _endButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.totalChildren - MAX_CHILDREN
        if fromIndex < 0:
            fromIndex = 0
        self.sendReqNodeMsg(self._nodeStruct.node.nodeID, fromIndex)

    # noinspection PyUnusedLocal
    def _closeButtonOnClick(self, widget):
        self._app.setFSBox(self._app.mainFSBox)

    def sendReqNodeMsg(self, nodeID: NodeID, fromIndex: int) -> None:
        msg = BiIntegerMsg(value1=nodeID, value2=fromIndex, fromID=self._app.id,
                           typeID=MsgID.REQ_NODE,
                           forID=self._sourcePart.sourceID)
        self._app.dispatcher.distribute(msg)

    def sendPlayNodeMsg(self, nodeID: NodeID) -> None:
        msg = IntegerMsg(value=nodeID, fromID=self._app.id,
                         typeID=MsgID.PLAY_NODE,
                         forID=self._sourcePart.sourceID)
        self._app.dispatcher.distribute(msg)

    def sendReqParentNodeMsg(self, nodeID: NodeID) -> None:
        msg = IntegerMsg(value=nodeID, fromID=self._app.id,
                         typeID=MsgID.REQ_PARENT_NODE,
                         forID=self._sourcePart.sourceID)
        self._app.dispatcher.distribute(msg)

    def _createTrackBox(self, width: int, height: int) -> gui.Widget:
        return SimpleTrackBox(width=width, height=height, app=self._app, sourcePart=self._sourcePart)

    def drawStruct(self, nodeStruct: NodeStruct) -> None:
        self._updateRequestRootButton(nodeStruct)
        self._nodeStruct = nodeStruct  # type: NodeStruct
        self._updateControls()
        if self._nodeStruct != EMPTY_NODE_STRUCT:
            self._fillStructBox(self._structBox)

    def _updateRequestRootButton(self, nodeStruct: NodeStruct) -> None:
        if nodeStruct == EMPTY_NODE_STRUCT:
            # some info has arrived, no need to show the request button
            self._structBox.append(self._requestRootButton)
        else:
            self._structBox.remove_child(self._requestRootButton)

    def _updateControls(self) -> None:
        notAtBegin = self._nodeStruct.fromChildIndex > 0
        self._homeButton.set_enabled(notAtBegin)
        self._prevButton.set_enabled(notAtBegin)

        notAtEnd = self._nodeStruct.totalChildren > (self._nodeStruct.fromChildIndex + MAX_CHILDREN)
        self._nextButton.set_enabled(notAtEnd)
        self._endButton.set_enabled(notAtEnd)
        if self._nodeStruct.totalChildren > 0:
            self._endButton.set_text("END " + str(self._nodeStruct.totalChildren))

    def _fillStructBox(self, box: gui.Widget) -> None:
        box.empty()
        # root box
        box.append(RootBox(self._nodeStruct.rootNode, self._nodeStruct.totalParents, self._leftWidth, 20, self))
        # node box only if not root
        if self._nodeStruct.node.nodeID != self._nodeStruct.rootNode.nodeID:
            box.append(NodeBox(self._nodeStruct.node, self._nodeStruct.parentID,
                               self._leftWidth, 20, self))
        # list of child boxes
        if self._nodeStruct.fromChildIndex > 0:
            box.append(gui.Label("..."))
        order = 0
        for child in self._nodeStruct.children:
            order += 1
            box.append(ChildBox(child, self._nodeStruct.fromChildIndex + order,
                                self._leftWidth, 20, self))
        if self._nodeStruct.fromChildIndex + order < self._nodeStruct.totalChildren:
            box.append(gui.Label("..."))
        pass


class ANodeBox(gui.HBox, abc.ABC):
    def __init__(self, node: NodeItem, width: int, height: int, myBox: NodeSelectFSBox):
        gui.HBox.__init__(self, width=width, height=height, margin='0px auto')
        self._node = node
        self._myBox = myBox
        self.append(self._getLabelBox(width, height), '1')
        if self._node.isPlayable:
            # TODO - image
            self.append(self._getPlayButton(), '2')

    def _getPlayButton(self):
        playButton = gui.Button(text="Play")
        playButton.set_on_click_listener(self._playNodeOnClick)
        return playButton

    # noinspection PyUnusedLocal
    def _playNodeOnClick(self, widget):
        self._myBox.sendPlayNodeMsg(self._node.nodeID)

    # noinspection PyUnusedLocal
    def _openNodeOnClick(self, widget):
        self._myBox.sendReqNodeMsg(self._node.nodeID, 0)

    @abc.abstractmethod
    def _getLabelBox(self, width, height) -> gui.Widget:
        pass


class RootBox(ANodeBox):
    def __init__(self, node: NodeItem, totalParents: int, width: int, height: int,
                 myBox: NodeSelectFSBox):
        self._totalParents = totalParents
        super().__init__(node=node, width=width, height=height, myBox=myBox)

    def _getLabelBox(self, width, height):
        box = gui.HBox(width=width - 20, height=height, margin='0px auto')
        # index
        text = self._node.label
        if self._totalParents > 1:
            text += "-> (" + str(self._totalParents - 1) + ") ->"
        box.append(gui.Label(text=text), '1')
        box.set_on_click_listener(self._openNodeOnClick)
        return box


class NodeBox(ANodeBox):
    def __init__(self, node: NodeItem, parentID: NodeID, width: int, height: int,
                 myBox: NodeSelectFSBox):
        self._parentID = parentID
        super().__init__(node=node, width=width, height=height, myBox=myBox)

    def _getLabelBox(self, width, height):
        box = gui.HBox(width=width - 20, height=height, margin='0px auto')
        # index
        box.append(gui.Label(text=self._node.label), '1')
        box.set_on_click_listener(self._openParentNodeOnClick)
        return box

    # noinspection PyUnusedLocal
    def _openParentNodeOnClick(self, widget):
        self._myBox.sendReqParentNodeMsg(self._node.nodeID)


class ChildBox(ANodeBox):
    def __init__(self, node: NodeItem, index: int, width: int, height: int, myBox: NodeSelectFSBox):
        self._index = index
        super().__init__(node=node, width=width, height=height, myBox=myBox)

    def _getLabelBox(self, width, height):
        box = gui.HBox(width=width - 20, height=height, margin='0px auto')
        # index
        box.append(gui.Label(text=str(self._index) + ':'), '1')
        box.append(self._getIcon(self._node), '2')
        box.append(gui.Label(text=self._node.label), '3')
        if self._node.isLeaf:
            box.set_on_click_listener(self._playNodeOnClick)
        else:
            box.set_on_click_listener(self._openNodeOnClick)
        return box

    @staticmethod
    def _getIcon(node: NodeItem) -> gui.Widget:
        # TODO - image
        text = "F" if node.isLeaf else "D"
        return gui.Label(text=text)