import logging
import sys
from typing import TYPE_CHECKING

import globalvars

if TYPE_CHECKING:
    from msgconsumer import MsgConsumer


def exitHandler(signum, frame):
    exitCleanly(0)


def exitCleanly(exitValue: int):
    logging.debug("Exiting...")
    for consumer in globalvars.msgConsumers:
        consumer = consumer  # type: MsgConsumer
        consumer.close()
        if consumer.is_alive():
            consumer.join(0.1)
    sys.exit(exitValue)
