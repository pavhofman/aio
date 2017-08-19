from typing import TYPE_CHECKING

from remi import gui

if TYPE_CHECKING:
    from uis.webapp import WebApp


class OverviewPanel(gui.Widget):
    def __init__(self, app: 'WebApp'):
        super().__init__(width=70, layout_orientation=gui.Widget.LAYOUT_VERTICAL)
        self._app = app
        self.style['text-align'] = 'center'
        self._sourcesPanel = self._getSourcesOverviewPanel()
        self.append(self._sourcesPanel)
        self._settingsBtn = gui.Button(text="Settings")
        self._settingsBtn.set_on_click_listener(self._onSettingsButtonPressed)
        self.append(self._settingsBtn)
        self._volumeBtn = gui.Button(text="??", width=60, height=60)
        self._volumeBtn.set_on_click_listener(self._onVolButtonPressed)
        self.append(self._volumeBtn)

    def setVolume(self, value: int):
        self._volumeBtn.set_text(str(value))

    def _getSourcesOverviewPanel(self) -> gui.Widget:
        panel = gui.Widget()
        for source in self._app.sourceParts:
            panel.append(source.getOverviewLabel())
        panel.set_on_click_listener(self._onSourcesPanelClicked)
        return panel

    # noinspection PyUnusedLocal
    def _onSourcesPanelClicked(self, widget):
        self._app.showActivateSourceFSBox()

    def _onSettingsButtonPressed(self, widget):
        pass

    # noinspection PyUnusedLocal
    def _onVolButtonPressed(self, widget):
        self._app.showVolFSBox()
