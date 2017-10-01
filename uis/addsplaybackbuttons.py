import abc
from typing import TYPE_CHECKING

from msgid import MsgID
from msgs.integermsg import IntegerMsg
from remi import gui
from sources.playbackstatus import PlaybackStatus
from sources.playcommand import PlayCommand
from uis.canappendwidget import CanAppendWidget

if TYPE_CHECKING:
    from uis.websourcepart import WebSourcePart
    from uis.webapp import WebApp

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


# noinspection PyAbstractClass
class AddsPlaybackButtons(CanAppendWidget, abc.ABC):
    """
    Class appends playback buttons and defines corresponding listener methods
    """

    def __init__(self, app: 'WebApp', sourcePart: 'WebSourcePart', showSkipBtns: bool = False):
        self._app = app
        self._sourcePart = sourcePart
        self._buttons = [
            self._createBtn(">", "12", PlayCommand.UNPAUSE),
            self._createBtn("II", "13", PlayCommand.PAUSE),
            self._createBtn("O", "14", PlayCommand.STOP),
        ]
        if showSkipBtns:
            self._buttons += [
                # posKeys - to the left
                self._createBtn("|<<", "10", PlayCommand.PREV),
                self._createBtn("<<", "11", PlayCommand.SB),
                # posKeys - to the right
                self._createBtn(">>", "15", PlayCommand.SF),
                self._createBtn(">>|", "16", PlayCommand.NEXT),
            ]

    def _createBtn(self, label: str, posKey: str, command: PlayCommand) -> CommandButton:
        btn = CommandButton(command, label)
        # all buttons are hidden initially
        btn.setVisible(False)
        btn.set_on_click_listener(self._onCommandBtnClicked)
        self.append(btn, posKey)
        return btn

    def _onCommandBtnClicked(self, widget: 'CommandButton'):
        self._sendPlayCommandMsg(widget.command)

    def _sendPlayCommandMsg(self, command: PlayCommand) -> None:
        msg = IntegerMsg(value=command.id, fromID=self._app.id,
                         typeID=MsgID.SOURCE_PLAY_COMMAND,
                         forID=self._sourcePart.sourceID)
        self._app.dispatcher.distribute(msg)

    def _updateButtonsFor(self, status: PlaybackStatus) -> None:
        for button in self._buttons:
            button.setVisible(button.command.isApplicableFor(status))

    def _hideButtons(self) -> None:
        for button in self._buttons:
            button.setVisible(False)
