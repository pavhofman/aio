from typing import List

from moduleid import ModuleID

msgConsumers = None  # type: List['MsgConsumer']
realSourceIDs = None  # type: List[ModuleID]
webAppRunning = False  # type: bool

stopWebApp = False  # type: bool
