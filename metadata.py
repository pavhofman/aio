from enum import Enum

"""
Metadata for inclusion in JSON of MsgID.METADATA_INFO 
"""


class Metadata(Enum):
    """
    value = key in JsonMsg JSON
    """
    TITLE = "T"
    # bitrate
    BITRATE = "B"
