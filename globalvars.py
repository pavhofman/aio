from threading import Event
from typing import List

from moduleid import ModuleID

msgConsumers = None  # type: List['MsgConsumer']
# flag for access to msgConsumers list
consumersReadyEvent = Event()

realSourceIDs = None  # type: List[ModuleID]
webAppRunning = False  # type: bool

stopWebApp = False  # type: bool

# for testing cooperation of web UIs,
# second WebUI on a different segment emulates the UI or remote control
# this parameter enables the second WebUI
startSecondWebUI = True
