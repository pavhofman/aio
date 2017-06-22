import logging
import sys

import globalvars


# noinspection PyUnusedLocal
def exitHandler(signum, frame):
    exitCleanly(0)


def exitCleanly(exitValue: int):
    logging.debug("Exiting...")
    for consumer in globalvars.msgConsumers:
        consumer.close()
        if consumer.is_alive():
            consumer.join(0.1)
    sys.exit(exitValue)