import abc
from typing import TYPE_CHECKING

from remi import gui

if TYPE_CHECKING:
    pass


class CanAppendWidget(abc.ABC):
    @abc.abstractmethod
    def append(self, value: gui.Widget, key=''):
        pass
