# list of message type IDs
from enum import Enum


class MsgID(Enum):
    # IntegerMsg(value=newVolume, forID=VolumeOperator)
    SET_VOL = 1

    # IntegerMsg(value=currentVolume, groupID=UIs)
    CURRENT_VOL_INFO = 2

    # RequestMsg(forID=VolumeOperator)
    REQ_CURRENT_VOL_INFO = 3

    # RequestMsg(groupID=Sources)
    REQ_SOURCE_STATUS = 4

    # Sent to all UIs by a source upon reception of REQ_SOURCE_STATUS msg or detection of status change
    # IntegerMsg(value=SourceStatus, fromID=source, groupID=UIs)
    SOURCE_STATUS_INFO = 5

    # not used yet. IntegerMsg sent to a particular source, value = requested statusID
    # can be used for deactivating source too, but more reliable method is ACTIVATE_SOURCE
    # IntegerMsg(value=SourceStatus, forID=Source)
    SET_SOURCE_STATUS = 6

    # IntegerMsg for all sources, value = ModID of activated source or 0 for deactivating all sources
    # if source detect change of its status, it will send SOURCE_STATUS msg to all UIs.
    # IntegerMsg(value=sourceID, groupID=Sources)
    ACTIVATE_SOURCE = 7
