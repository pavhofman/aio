import abc
from typing import TYPE_CHECKING, Callable

from msgid import MsgID
from msgs.integermsg import IntegerMsg
from remi import gui
from sources.playbackstatus import PlaybackStatus
from sources.playcommand import PlayCommand
from uis.canappendwidget import CanAppendWidget

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp


# noinspection PyAbstractClass
class AddsPlaybackButtons(CanAppendWidget, abc.ABC):
    """
    Class appends playback buttons and defines corresponding listener methods
    """

    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart'):
        self._app = app
        self._sourcePart = sourcePart

        self._playBtn = createBtn(">", PlayCommand.UNPAUSE, self._onCommandBtnClicked)
        self.append(self._playBtn, "10")
        self._pauseBtn = createBtn("II", PlayCommand.PAUSE, self._onCommandBtnClicked)
        self.append(self._pauseBtn, "11")
        self._stopBtn = createBtn("O", PlayCommand.STOP, self._onCommandBtnClicked)
        self.append(self._stopBtn, "12")

    def _onCommandBtnClicked(self, widget: 'CommandButton'):
        self._sendPlayCommandMsg(widget.command)

    def _sendPlayCommandMsg(self, command: PlayCommand) -> None:
        msg = IntegerMsg(value=command.id, fromID=self._app.id,
                         typeID=MsgID.SOURCE_PLAY_COMMAND,
                         forID=self._sourcePart.sourceID)
        self._app.dispatcher.distribute(msg)

    def _updateButtonsFor(self, status: PlaybackStatus) -> None:
        for button in [self._playBtn, self._pauseBtn, self._stopBtn]:
            button.setVisible(button.command.isApplicableFor(status))

    def _hideButtons(self) -> None:
        for button in [self._playBtn, self._pauseBtn, self._stopBtn]:
            button.setVisible(False)


HIDDEN_ATTRIB = 'hidden'


class CommandButton(gui.Button):
    def __init__(self, command: PlayCommand, text='', **kwargs):
        super().__init__(text, **kwargs)
        self.command = command

    def setVisible(self, visible: bool) -> None:
        isHidden = HIDDEN_ATTRIB in self.attributes.keys()
        if visible and isHidden:
            del self.attributes[HIDDEN_ATTRIB]
        elif not visible and not isHidden:
            self.attributes[HIDDEN_ATTRIB] = HIDDEN_ATTRIB


def createBtn(label: str, command: PlayCommand, listenerFn: Callable) -> CommandButton:
    btn = CommandButton(command, label)
    # all buttons are hidden initially
    btn.setVisible(False)
    btn.set_on_click_listener(listenerFn)
    return btn
