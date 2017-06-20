from queue import Empty
from typing import Optional, TYPE_CHECKING

from remi import gui

import globals
from moduleid import ModuleID
from msgid import MsgID
from msgs.integermsg import IntegerMsg
from msgs.message import Message
from uis.timedclose import TimedClose
from uis.volumeslider import VolumeSlider

if TYPE_CHECKING:
    from uis.webapp import WebApp

# the container gets closed after TIMEOUT of no activity
TIMEOUT = 2


class VolumeFSContainer(gui.Widget, TimedClose):
    def __init__(self, app: 'WebApp'):
        TimedClose.__init__(self, app=app, timeout=1)
        gui.Widget.__init__(self, width=app.getWidth(), height=app.getHeight(), margin='0px auto',
                            layout_orientation=gui.Widget.LAYOUT_HORIZONTAL)
        self._app = app
        self.style['display'] = 'red'
        self.style['overflow'] = 'hidden'
        self._volumeSlider = self._getVolumeSlider()
        self.append(self._volumeSlider)
        self._volumeContLabel = gui.Label('', width=20, height=30, margin='10px')
        self._volumeContLabel.set_text(self._volumeSlider.get_value())
        self.append(self._volumeContLabel)

    def setVolume(self, value: int):
        self._volumeSlider.set_value(value)
        self._volumeContLabel.set_text(str(value))

    def _getVolumeSlider(self) -> VolumeSlider:
        volumeSlider = VolumeSlider(str(0), 0, 100, 1, width=self._app.getWidth() - 40, height=50, margin='10px')
        volumeSlider.set_on_change_listener(self._volSliderChanged)
        volumeSlider.set_on_mousedown_listener(self._volSliderMouseDown)
        volumeSlider.set_on_mouseup_listener(self._volSliderMouseUp)
        volumeSlider.set_oninput_listener(self._volSliderInput)
        return volumeSlider

    # noinspection PyUnusedLocal
    def _volSliderChanged(self, widget, value):
        self._app.setVolume(value)
        self._sendVolume(value)

    # noinspection PyUnusedLocal
    def _volSliderInput(self, widget, value):
        # TODO - changing color
        self._volumeContLabel.set_text(str(value))

    # noinspection PyUnusedLocal
    def _volSliderMouseDown(self, emitter, x, y):
        self.closeTimer()

    # noinspection PyUnusedLocal
    def _volSliderMouseUp(self, emitter, x, y):
        self._startTimer()

    @staticmethod
    def _readMsg() -> Optional[Message]:
        try:
            msg = globals.webQueue.get_nowait()
            return msg
        except Empty:
            return None

    def _sendVolume(self, value: int):
        msg = IntegerMsg(value=value, fromID=self._app.getID(), typeID=MsgID.SET_VOL, forID=ModuleID.VOLUME_OPERATOR)
        self._app.getDispatcher().distribute(msg)
