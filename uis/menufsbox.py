from typing import TYPE_CHECKING

from msgs.nodemsg import NodeItem
from remi import gui
from uis.utils import createBtn

if TYPE_CHECKING:
    from uis.webapp import WebApp

"""
Menu box for NodeItem controls/detailed information
"""


class MenuFSBox(gui.VBox):
    def __init__(self, app: 'WebApp', node: NodeItem):
        gui.VBox.__init__(self, width=app.getWidth(), height=app.getHeight(), margin='0px auto')
        self._node = node
        self._app = app
        # all the way down
        self.append(createBtn("CLOSE", True, self._closeButtonOnClick), "100")

    # noinspection PyUnusedLocal
    def _closeButtonOnClick(self, widget):
        self._app.showPrevFSBox()
