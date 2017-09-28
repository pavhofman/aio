#!/usr/bin/python3

# usage: python control.py
#
import logging
import signal
import time
from typing import List

import globalvars
from dispatcher import Dispatcher
from exiting import exitHandler, exitCleanly
from groupid import GroupID
from heartbeat import Heartbeat
from moduleid import ModuleID
from serialreciever import SerialReciever
from serialsender import SerialSender
from sources.analogsource import AnalogSource
from sources.cdsource import CDSource
from sources.filesource import FileSource
from sources.radiosource import RadioSource
from uis.inputconsoleui import InputConsoleUI
from uis.webui import WebUI
from volumeoperator import VolumeOperator

"""
PC:
    UI_CONSOLE
    FILE_SOURCE
    TO_MAIN_MCU_SENDER
    FROM_MAIN_MCU_RECEIVER

MAIN_MCU:
    VOLUME_OP
    ANALOG_SOURCE
    UI_MAIN_DISPLAY    
    TO_PC_SENDER
    FROM_PC_RECEIVER
    
RC: zatim nic
"""

routeMapOnPC = {
    ModuleID.WEBUI_PC: ModuleID.WEBUI_PC,
    ModuleID.FILE_SOURCE: ModuleID.FILE_SOURCE,
    ModuleID.RADIO_SOURCE: ModuleID.RADIO_SOURCE,
    ModuleID.CD_SOURCE: ModuleID.CD_SOURCE,
    ModuleID.TO_MAIN_MCU_SENDER: ModuleID.TO_MAIN_MCU_SENDER,
    ModuleID.FROM_MAIN_MCU_RECEIVER: ModuleID.FROM_MAIN_MCU_RECEIVER,

    ModuleID.VOLUME_OPERATOR: ModuleID.TO_MAIN_MCU_SENDER,
    ModuleID.ANALOG_SOURCE: ModuleID.TO_MAIN_MCU_SENDER,
    ModuleID.TO_PC_SENDER: ModuleID.TO_MAIN_MCU_SENDER,
    ModuleID.FROM_PC_RECEIVER: ModuleID.TO_MAIN_MCU_SENDER,
    ModuleID.UI_MAIN_DISPLAY: ModuleID.TO_MAIN_MCU_SENDER,
}

routeMapOnMCU = {
    ModuleID.VOLUME_OPERATOR: ModuleID.VOLUME_OPERATOR,
    ModuleID.ANALOG_SOURCE: ModuleID.ANALOG_SOURCE,
    ModuleID.TO_PC_SENDER: ModuleID.TO_PC_SENDER,
    ModuleID.FROM_PC_RECEIVER: ModuleID.FROM_PC_RECEIVER,
    ModuleID.UI_MAIN_DISPLAY: ModuleID.UI_MAIN_DISPLAY,

    ModuleID.WEBUI_PC: ModuleID.TO_PC_SENDER,
    ModuleID.FILE_SOURCE: ModuleID.TO_PC_SENDER,
    ModuleID.RADIO_SOURCE: ModuleID.TO_PC_SENDER,
    ModuleID.CD_SOURCE: ModuleID.TO_PC_SENDER,
    ModuleID.TO_MAIN_MCU_SENDER: ModuleID.TO_PC_SENDER,
    ModuleID.FROM_MAIN_MCU_RECEIVER: ModuleID.TO_PC_SENDER,
}

groupMapOnPC = {
    GroupID.UI: [ModuleID.WEBUI_PC, ModuleID.TO_MAIN_MCU_SENDER],
    GroupID.SOURCE: [ModuleID.FILE_SOURCE, ModuleID.RADIO_SOURCE,
                     ModuleID.CD_SOURCE, ModuleID.TO_MAIN_MCU_SENDER],
}

groupMapOnMCU = {
    GroupID.UI: [ModuleID.UI_MAIN_DISPLAY, ModuleID.TO_PC_SENDER],
    GroupID.SOURCE: [ModuleID.ANALOG_SOURCE, ModuleID.TO_PC_SENDER],
}

# list of all real sources modIDs
globalvars.realSourceIDs = [ModuleID.ANALOG_SOURCE, ModuleID.FILE_SOURCE, ModuleID.RADIO_SOURCE,
                            ModuleID.CD_SOURCE]  # type: List[ModuleID]

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
    signal.signal(signal.SIGINT, exitHandler)
    signal.signal(signal.SIGTERM, exitHandler)
    try:
        dispatcherOnPC = Dispatcher("On PC", routeMap=routeMapOnPC, groupMap=groupMapOnPC)
        dispatcherOnMCU = Dispatcher("On MCU", routeMap=routeMapOnMCU, groupMap=groupMapOnMCU)

        receiverOnPC = SerialReciever(
            id=ModuleID.FROM_MAIN_MCU_RECEIVER, dispatcher=dispatcherOnPC, mySideSenderID=ModuleID.TO_MAIN_MCU_SENDER)
        receiverOnMCU = SerialReciever(
            id=ModuleID.FROM_PC_RECEIVER, dispatcher=dispatcherOnMCU, mySideSenderID=ModuleID.TO_PC_SENDER)

        senderOnPC = SerialSender(
            id=ModuleID.TO_MAIN_MCU_SENDER, dispatcher=dispatcherOnPC, otherSideReceiver=receiverOnMCU)
        senderOnMCU = SerialSender(
            id=ModuleID.TO_PC_SENDER, dispatcher=dispatcherOnMCU, otherSideReceiver=receiverOnPC)

        globalvars.msgConsumers = [
            VolumeOperator(dispatcherOnMCU),
            WebUI(id=ModuleID.WEBUI_PC, dispatcher=dispatcherOnPC),
            InputConsoleUI(id=ModuleID.UI_MAIN_DISPLAY, dispatcher=dispatcherOnMCU),
            AnalogSource(dispatcherOnMCU),
            FileSource(dispatcherOnPC),
            RadioSource(dispatcherOnPC),
            CDSource(dispatcherOnPC),
            senderOnPC,
            senderOnMCU,
            receiverOnPC,
            receiverOnMCU,
            Heartbeat(dispatcher=dispatcherOnMCU)
        ]
        globalvars.consumersReadyEvent.set()
        while True:
            time.sleep(5)
            # dispatcherOnPC.printStats()
            # dispatcherOnMCU.printStats()
            pass
    except Exception as e:
        logging.error(e, exc_info=True)
        exitCleanly(1)
