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

    # IntegerMsg for all sources, value = ModID of activated source or 0 for deactivating all sources
    # if source detect change of its status, it will send SOURCE_STATUS msg to all UIs.
    # IntegerMsg(value=sourceID, groupID=Sources)
    ACTIVATE_SOURCE = 6

    # IntegerMsg sent to a particular source, value = requested nodeID
    # IntegerMsg(value=NodeID, forID=source)
    PLAY_NODE = 7

    # IntegerMsg sent to a particular source, value = requested Playback
    # IntegerMsg(value=Playback, forID=Source)
    SET_SOURCE_PLAYBACK = 8

    # Sent to all UIs by a source upon detection of playback change
    # IntegerMsg(value=playbackID, fromID=source, groupID=UIs)
    SOURCE_PLAYBACK_INFO = 9

    # BiIntegerMsg(value1 = nodeID, value2 = fromIndex, forID=source)
    # request for node nodeID with 5 children, starting from fromIndex
    # Used for vertical traversing the tree
    REQ_NODE = 10

    # IntegerMsg(value = nodeID, forID=source)
    # request for parent node info of nodeID with 5 children, starting from nodeID index - 1
    # Used for horizontal traversing the tree
    REQ_PARENT_NODE = 11

    # NodeMsg(fromID: corresponding sourceID, groupID:UIs)
    NODE_INFO = 12

    # BiIntegerMsg(value1 = nodeID, value2 = timepos in seconds, fromID=source, forID=UI)
    TIME_POS_INFO = 13
