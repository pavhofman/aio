import abc
from typing import TYPE_CHECKING, List

from msgs.nodemsg import NodeStruct, NodeItem, NON_EXISTING_NODE_ID, NodeID
from msgs.trackmsg import TrackItem
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
        self.__trackBox = self._createTrackBox(self._leftWidth, CUR_TRACK_HEIGHT)
        leftBox = gui.VBox(width=self._leftWidth, height=app.getHeight(), margin='0px auto')
        leftBox.append(self._structBox, '1')
        leftBox.append(self.__trackBox, '2')
        self.append(leftBox, '1')
        self.append(self._controlsBox, '2')
        # currently displayed node in selector
        self._nodeStruct = EMPTY_NODE_STRUCT
        # list of rendered child boxes
        self._childBoxes = []  # type: List[ChildBox]
        self.clear()

    def clear(self):
        self._nodeStruct = EMPTY_NODE_STRUCT
        self._updateControls()
        self._structBox.empty()
        self.__trackBox.clear()
        self._childBoxes.clear()

        self.drawStruct(EMPTY_NODE_STRUCT)

    def _createStructBox(self, width: int, height: int) -> gui.Widget:
        return gui.VBox(width=width, height=height, margin='0px auto')

    def sendReqRootNodeMsg(self):
        self._sourcePart.sendReqNodeMsg(NON_EXISTING_NODE_ID, 0)

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
        self._sourcePart.sendReqNodeMsg(self._nodeStruct.node.nodeID, 0)

    # noinspection PyUnusedLocal

    def _prevButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.fromChildIndex - MAX_CHILDREN
        if fromIndex < 0:
            fromIndex = 0
        self._sourcePart.sendReqNodeMsg(self._nodeStruct.node.nodeID, fromIndex)

    # noinspection PyUnusedLocal

    def _nextButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.fromChildIndex + MAX_CHILDREN
        lastFromIndex = self._nodeStruct.totalChildren - MAX_CHILDREN
        if fromIndex > lastFromIndex:
            fromIndex = lastFromIndex
        self._sourcePart.sendReqNodeMsg(self._nodeStruct.node.nodeID, fromIndex)

    # noinspection PyUnusedLocal

    # noinspection PyUnusedLocal
    def _endButtonOnClick(self, widget):
        fromIndex = self._nodeStruct.totalChildren - MAX_CHILDREN
        if fromIndex < 0:
            fromIndex = 0
        self._sourcePart.sendReqNodeMsg(self._nodeStruct.node.nodeID, fromIndex)

    # noinspection PyUnusedLocal
    def _closeButtonOnClick(self, widget):
        self._app.setFSBox(self._app.mainFSBox)

    def _createTrackBox(self, width: int, height: int) -> SimpleTrackBox:
        return SimpleTrackBox(width=width, height=height, sourcePart=self._sourcePart)

    def hasDataFromSource(self) -> bool:
        return self._nodeStruct != EMPTY_NODE_STRUCT

    def drawStruct(self, nodeStruct: NodeStruct) -> None:
        self._nodeStruct = nodeStruct  # type: NodeStruct
        self._updateControls()
        self._fillStructBox(self._structBox)

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
        self._childBoxes.clear()
        order = 0
        for child in self._nodeStruct.children:
            order += 1
            childBox = ChildBox(child, self._nodeStruct.fromChildIndex + order, self._leftWidth, 20, self)
            if self.__shouldMarkPlaying(child):
                childBox.setPlaying(True)

            box.append(childBox)
            self._childBoxes.append(childBox)
        if self._nodeStruct.fromChildIndex + order < self._nodeStruct.totalChildren:
            box.append(gui.Label("..."))
        pass

    def __shouldMarkPlaying(self, nodeItem: NodeItem) -> bool:
        playingTrackItem = self._sourcePart._playingTrackItem
        return playingTrackItem is not None \
               and playingTrackItem.nodeID == nodeItem.nodeID

    def drawTrack(self, trackItem: TrackItem) -> None:
        self.__trackBox.drawTrack(trackItem)
        self.__markPlayingChildBox(trackItem)

    def __markPlayingChildBox(self, trackItem):
        for childBox in self._childBoxes:
            if childBox._node.nodeID == trackItem.nodeID:
                childBox.setPlaying(True)
            else:
                childBox.setPlaying(False)

    def drawPlaybackStopped(self) -> None:
        self.__trackBox.drawPlaybackStopped()
        # clearing all childBox playmarks
        for childBox in self._childBoxes:
            childBox.setPlaying(False)

    def drawPlaybackPaused(self) -> None:
        self.__trackBox.drawPlaybackPaused()

    def drawPlaybackPlaying(self) -> None:
        self.__trackBox.drawPlaybackPlaying()


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
        self._myBox._sourcePart.sendPlayNodeMsg(self._node.nodeID)

    # noinspection PyUnusedLocal
    def _openNodeOnClick(self, widget):
        self._myBox._sourcePart.sendReqNodeMsg(self._node.nodeID, 0)

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
        self._myBox._sourcePart.sendReqParentNodeMsg(self._node.nodeID)


class ChildBox(ANodeBox):
    def __init__(self, node: NodeItem, index: int, width: int, height: int, myBox: NodeSelectFSBox):
        self._index = index
        self.__isPlaying = False
        self.__playingMark = gui.Label("")
        super().__init__(node=node, width=width, height=height, myBox=myBox)

    def _getLabelBox(self, width, height):
        box = gui.HBox(width=width - 20, height=height, margin='0px auto')
        # index
        box.append(self.__playingMark, '0')
        box.append(gui.Label(text=str(self._index) + ':'), '1')
        box.append(self._getIcon(self._node), '2')
        box.append(gui.Label(text=self._node.label), '3')
        if self._node.isLeaf:
            box.set_on_click_listener(self._playNodeOnClick)
        else:
            box.set_on_click_listener(self._openNodeOnClick)
        return box

    def setPlaying(self, isPlaying: bool) -> None:
        if self.__isPlaying != isPlaying:
            self.__isPlaying = isPlaying
            self.__playingMark.set_text('*' if isPlaying else '')

    @staticmethod
    def _getIcon(node: NodeItem) -> gui.Widget:
        # TODO - image
        text = "F" if node.isLeaf else "D"
        return gui.Label(text=text)
