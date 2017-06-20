from remi import gui

from uis.statusdecoration import StatusDecoration


class StatusButton(gui.Button, StatusDecoration):
    def __init__(self, text='', **kwargs):
        gui.Button.__init__(self, text, **kwargs)
        StatusDecoration.__init__(self)


class StatusLabel(gui.Label, StatusDecoration):
    def __init__(self, text='', **kwargs):
        gui.Label.__init__(self, text, **kwargs)
        StatusDecoration.__init__(self)
