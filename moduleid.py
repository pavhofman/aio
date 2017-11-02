# IDs of all modules within the system
from enum import Enum


class ModuleID(Enum):
    ANY = 0
    ANALOG_SOURCE = 1
    FILE_SOURCE = 2
    VOLUME_OPERATOR = 3
    WEBUI_PC = 4
    MCU_PC_SENDER = 5
    PC_MCU_RECEIVER = 6
    UI_CONSOLE = 7
    PC_MCU_SENDER = 8
    MCU_PC_RECEIVER = 9
    HEARTBEAT = 10
    RADIO_SOURCE = 11
    CD_SOURCE = 12
    MCU_RC_SENDER = 13
    RC_MCU_RECEIVER = 14
    RC_MCU_SENDER = 15
    MCU_RC_RECEIVER = 16
    WEBUI_RC = 17
