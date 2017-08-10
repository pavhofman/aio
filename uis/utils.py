from typing import Callable

from remi import gui


def createBtn(label: str, enabled: bool, listenerFn: Callable) -> gui.Button:
    btn = gui.Button(label)
    btn.set_enabled(enabled)
    btn.set_on_click_listener(listenerFn)
    return btn
