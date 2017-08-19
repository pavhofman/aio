# IDs of all modules within the system
from enum import Enum


class ModuleID(Enum):
    ANY = 0
    ANALOG_SOURCE = 1
    FILE_SOURCE = 2
    VOLUME_OPERATOR = 3
    WEBUI_PC = 4
    TO_PC_SENDER = 5
    FROM_PC_RECEIVER = 6
    UI_MAIN_DISPLAY = 7
    TO_MAIN_MCU_SENDER = 8
    FROM_MAIN_MCU_RECEIVER = 9
    HEARTBEAT = 10  # warning - the id is not routable, heartbeat does not listen to incoming messages
    RADIO_SOURCE = 11
