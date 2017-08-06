from remi import gui

from sources.sourcestatus import SourceStatus


class StatusDecoration:
    def __init__(self: gui.Widget):
        self.style['color'] = 'black'

    def decorateForStatus(self, status: SourceStatus) -> None:
        self._setStyle(status)
        self._setEnabled(status)

    def _setStyle(self: gui.Widget, status: SourceStatus) -> None:
        if status == SourceStatus.UNAVAILABLE:
            self.style['background'] = 'gray'
        elif status == SourceStatus.ACTIVATED:
            self.style['background'] = 'yellow'
        else:
            # not_activated
            self.style['background'] = 'white'

    def _setEnabled(self: gui.Widget, status: SourceStatus) -> None:
        if status.isAvailable():
            self.set_enabled(True)
        else:
            self.set_enabled(False)
