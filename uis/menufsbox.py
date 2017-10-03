from typing import TYPE_CHECKING

from msgs.nodemsg import NodeItem, isBookmark
from remi import gui
from uis.utils import createBtn

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp

"""
Menu box for NodeItem controls/detailed information
"""
BOOKMARK_BTN_POSKEY = "10"


class MenuFSBox(gui.VBox):
    def __init__(self, sourcePart: 'WebSourcePart', node: NodeItem, isRoot: bool):
        self._sourcePart = sourcePart
        self._node = node
        gui.VBox.__init__(self, width=self._getApp().getWidth(), height=self._getApp().getHeight(), margin='0px auto')
        self.append(gui.Label(node.label), "1")
        if not isRoot:
            # bookmarking root makes no sense
            self.append(self._getBookmarkBtn(), BOOKMARK_BTN_POSKEY)
        # all the way down
        self.append(createBtn("CLOSE", True, self._closeButtonOnClick), "100")

    def _getBookmarkBtn(self) -> gui.Button:
        if isBookmark(self._node.bookmarkID):
            return createBtn("Delete bookmark", True, self._deleteBookmarkOnClick)
        else:
            return createBtn("Create bookmark", True, self._createBookmarkOnClick)

    # noinspection PyUnusedLocal
    def _closeButtonOnClick(self, widget):
        self._getApp().showPrevFSBox()

    # noinspection PyUnusedLocal
    def _createBookmarkOnClick(self, widget):
        self._sourcePart.sendCreateBookmarkMsg(self._node.nodeID)
        self.remove_child(widget)
        self.append(gui.Label("Creating bookmark..."), BOOKMARK_BTN_POSKEY)

    # noinspection PyUnusedLocal
    def _deleteBookmarkOnClick(self, widget):
        self._sourcePart.sendDeleteBookmarkMsg(self._node.nodeID)
        self.remove_child(widget)
        self.append(gui.Label("Deleting bookmark..."), BOOKMARK_BTN_POSKEY)

    def _getApp(self) -> 'WebApp':
        return self._sourcePart._app
