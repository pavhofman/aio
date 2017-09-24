from threading import Event
from typing import List

from moduleid import ModuleID

msgConsumers = None  # type: List['MsgConsumer']
# flag for access to msgConsumers list
consumersReadyEvent = Event()

realSourceIDs = None  # type: List[ModuleID]
webAppRunning = False  # type: bool

stopWebApp = False  # type: bool
