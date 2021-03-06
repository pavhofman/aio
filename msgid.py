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
    # IntegerMsg(value=SourceStatusID, fromID=source, groupID=UIs)
    SOURCE_STATUS_INFO = 5

    # IntegerMsg for all sources, value = ModID of activated source or 0 for deactivating all sources
    # if source detect change of its status, it will send SOURCE_STATUS msg to all UIs.
    # IntegerMsg(value=sourceID, groupID=Sources)
    ACTIVATE_SOURCE = 6

    # IntegerMsg sent to a particular source, value = requested nodeID
    # IntegerMsg(value=NodeID, forID=source)
    PLAY_NODE = 7

    # IntegerMsg sent to a particular source, value = requested PlayCommand
    # IntegerMsg(value=PlayCommandID, forID=Source)
    SOURCE_PLAY_COMMAND = 8

    # Sent to all UIs by a source upon detection of playback change
    # IntegerMsg(value=playbackStatusID, fromID=source, groupID=UIs)
    SOURCE_PLAYBACK_INFO = 9

    # BiIntegerMsg(value1 = nodeID, value2 = fromIndex, forID=source)
    # request for node structure of nodeID with 5 children, starting from fromIndex
    # Used for vertical traversing the tree
    REQ_NODE = 10

    # IntegerMsg(value = nodeID, forID=source)
    # request for parent node info of nodeID with 5 children, starting from nodeID index - 1
    # Used for horizontal traversing the tree
    REQ_PARENT_NODE = 11

    # NodeMsg(fromID: corresponding sourceID, groupID:UIs)
    NODE_INFO = 12

    # BiIntegerMsg(value1 = timepos in seconds, value2 = duration in seconds, fromID=source, forID=UI)
    TIME_POS_INFO = 13

    # TrackMsg(trackItem, fromID=source, forID=UI)
    TRACK_INFO = 14

    # AudioParamsMsg(paramsItem, fromID=source, forID=UI)
    AUDIOPARAMS_INFO = 15

    # JsonMsg(json=json_with_relevant_metadata, fromID=source, forID=UI)
    METADATA_INFO = 16

    # IntegerMsg(value = nodeID, forID=source)
    # request for bookmark creation
    CREATE_NODE_BOOKMARK = 17

    # IntegerMsg(value = nodeID, forID=source)
    # request for bookmark deletion
    DELETE_NODE_BOOKMARK = 18

    # IntegerMsg(value = bitmapped groupIDs)
    # informs dispatchers about groups of the sender
    IN_GROUPS_MSG = 19
