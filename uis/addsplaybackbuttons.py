import abc
from typing import TYPE_CHECKING

from msgid import MsgID
from msgs.integermsg import IntegerMsg
from sources.playbackstatus import PlaybackStatus
from uis.canappendwidget import CanAppendWidget
from uis.utils import createBtn

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

        self._playBtn = createBtn(">", False, self._onPlayBtnClicked)
        self.append(self._playBtn, "10")
        self._pauseBtn = createBtn("II", False, self._onPauseBtnClicked)
        self.append(self._pauseBtn, "11")
        self._stopBtn = createBtn("O", False, self._onStopBtnClicked)
        self.append(self._stopBtn, "12")

    # noinspection PyUnusedLocal
    def _onPlayBtnClicked(self, widget):
        self._sendPlaybackStatusMsg(PlaybackStatus.PLAYING)

    # noinspection PyUnusedLocal
    def _onPauseBtnClicked(self, widget):
        self._sendPlaybackStatusMsg(PlaybackStatus.PAUSED)

    # noinspection PyUnusedLocal
    def _onStopBtnClicked(self, widget):
        self._sendPlaybackStatusMsg(PlaybackStatus.STOPPED)

    def _sendPlaybackStatusMsg(self, status: PlaybackStatus) -> None:
        msg = IntegerMsg(value=status.value, fromID=self._app.id,
                         typeID=MsgID.SET_SOURCE_PLAYBACK,
                         forID=self._sourcePart.sourceID)
        self._app.dispatcher.distribute(msg)

    def drawPlaybackStopped(self) -> None:
        self._clearTrackInfo()
        self._playBtn.set_enabled(False)
        self._pauseBtn.set_enabled(False)
        self._stopBtn.set_enabled(False)

    def drawPlaybackPaused(self) -> None:
        self._playBtn.set_enabled(True)
        self._pauseBtn.set_enabled(False)
        self._stopBtn.set_enabled(True)

    def drawPlaybackPlaying(self) -> None:
        self._playBtn.set_enabled(False)
        self._pauseBtn.set_enabled(True)
        self._stopBtn.set_enabled(True)

    def _clearTrackInfo(self):
        pass
