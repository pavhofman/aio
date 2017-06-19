from typing import TYPE_CHECKING

from remi import gui

from uis.timedclose import TimedClose

if TYPE_CHECKING:
    from uis.webapp import WebApp


class SourceSelFSContainer(gui.Widget, TimedClose):
    def __init__(self, app: 'WebApp'):
        TimedClose.__init__(self, app=app)
        gui.Widget.__init__(self, width=app.getWidth(), height=app.getHeight(), margin='0px auto',
                            layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        self.style['display'] = 'red'
        self.style['overflow'] = 'hidden'
