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
Modules for each segment:
PC:
    FILE_SOURCE = 2
    RADIO_SOURCE = 11
    CD_SOURCE = 12
    WEBUI_PC = 4
    PC_MCU_SENDER = 8
    MCU_PC_RECEIVER = 9

MAIN_MCU:    
    MCU_PC_SENDER = 5
    PC_MCU_RECEIVER = 6
    ANALOG_SOURCE = 1
    VOLUME_OPERATOR = 3
    HEARTBEAT = 10
    MCU_RC_SENDER = 13
    RC_MCU_RECEIVER = 14

RC:    
    RC_MCU_SENDER = 15
    MCU_RC_RECEIVER = 16
    UI_CONSOLE = 7
    WEBUI_RC = 17

"""

# list of all real sources modIDs
globalvars.realSourceIDs = [ModuleID.ANALOG_SOURCE, ModuleID.FILE_SOURCE, ModuleID.RADIO_SOURCE,
                            ModuleID.CD_SOURCE]  # type: List[ModuleID]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
    signal.signal(signal.SIGINT, exitHandler)
    signal.signal(signal.SIGTERM, exitHandler)
    try:
        dispatcherOnPC = Dispatcher("On PC", gatewayIDs=[ModuleID.PC_MCU_SENDER])
        dispatcherOnMCU = Dispatcher("On MCU", gatewayIDs=[ModuleID.MCU_PC_SENDER, ModuleID.MCU_RC_SENDER])
        dispatcherOnRC = Dispatcher("On RC", gatewayIDs=[ModuleID.RC_MCU_SENDER])

        receiverMCU_PC = SerialReciever(
            id=ModuleID.MCU_PC_RECEIVER, name='MCU->PC', dispatcher=dispatcherOnPC,
            mySideSenderID=ModuleID.PC_MCU_SENDER)
        receiverPC_MCU = SerialReciever(
            id=ModuleID.PC_MCU_RECEIVER, name='PC->MCU', dispatcher=dispatcherOnMCU,
            mySideSenderID=ModuleID.MCU_PC_SENDER)
        receiverRC_MCU = SerialReciever(
            id=ModuleID.RC_MCU_RECEIVER, name='RC->MCU', dispatcher=dispatcherOnMCU,
            mySideSenderID=ModuleID.MCU_RC_SENDER)
        receiverMCU_RC = SerialReciever(
            id=ModuleID.MCU_RC_RECEIVER, name='MCU->RC', dispatcher=dispatcherOnRC,
            mySideSenderID=ModuleID.RC_MCU_SENDER)

        senderPC_MCU = SerialSender(
            id=ModuleID.PC_MCU_SENDER, name='PC->MCU', dispatcher=dispatcherOnPC, otherSideReceiver=receiverPC_MCU)
        senderMCU_PC = SerialSender(
            id=ModuleID.MCU_PC_SENDER, name='MCU->PC', dispatcher=dispatcherOnMCU, otherSideReceiver=receiverMCU_PC)
        senderMCU_RC = SerialSender(
            id=ModuleID.MCU_RC_SENDER, name='MCU->RC', dispatcher=dispatcherOnMCU, otherSideReceiver=receiverMCU_RC)
        senderRC_MCU = SerialSender(
            id=ModuleID.RC_MCU_SENDER, name='RC->MCU', dispatcher=dispatcherOnRC, otherSideReceiver=receiverRC_MCU)

        globalvars.msgConsumers = [
            senderPC_MCU,
            senderMCU_PC,
            senderMCU_RC,
            senderRC_MCU,
            receiverMCU_PC,
            receiverPC_MCU,
            receiverRC_MCU,
            receiverMCU_RC,
            VolumeOperator(dispatcherOnMCU),
            WebUI(id=ModuleID.WEBUI_PC, name='WebUI PC', dispatcher=dispatcherOnPC, port=8081),
            InputConsoleUI(id=ModuleID.UI_CONSOLE, dispatcher=dispatcherOnRC),
            AnalogSource(dispatcherOnMCU),
            FileSource(dispatcherOnPC),
            RadioSource(dispatcherOnPC),
            CDSource(dispatcherOnPC),
            Heartbeat(dispatcher=dispatcherOnMCU)
        ]
        if globalvars.startSecondWebUI:
            globalvars.msgConsumers.append(
                WebUI(id=ModuleID.WEBUI_RC, name='WebUI RC', dispatcher=dispatcherOnRC, port=8082)
            )
        globalvars.consumersReadyEvent.set()
        while True:
            time.sleep(5)
            # dispatcherOnPC.printStats()
            # dispatcherOnMCU.printStats()
            pass
    except Exception as e:
        logging.error(e, exc_info=True)
        exitCleanly(1)
