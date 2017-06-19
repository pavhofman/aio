import logging
import sys

import globals


# noinspection PyUnusedLocal
def exitHandler(signum, frame):
    exitCleanly(0)


def exitCleanly(exitValue: int):
    logging.debug("Exiting...")
    for consumer in globals.msgConsumers:
        consumer.close()
        if consumer.is_alive():
            consumer.join(0.1)
    sys.exit(exitValue)