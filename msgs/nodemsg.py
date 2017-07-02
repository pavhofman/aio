from typing import List, NewType

from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message

NodeID = NewType('NodeID', int)
NON_EXISTING_NODE_ID = 0


class NodeMsg(Message):
    """
    Msg with node information
    """

    def __init__(self, nodeStruct: 'NodeStruct',
                 fromID: ModuleID, typeID: MsgID, forID=ModuleID.ANY, groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=typeID, forID=forID, groupID=groupID)
        self.nodeStruct = nodeStruct

    def __str__(self) -> str:
        return super().__str__() + "; " + str(self.nodeStruct)


class NodeItem:
    """
    Item for the Node, data container between Source and UI
    """

    def __init__(self, nodeID: NodeID, label: str, isPlayable: bool, isLeaf: bool):
        # fixed ID tracked by the source. Used to streamline the messages
        self.nodeID = nodeID
        # shown in the UI
        self.label = label
        # whether to offer playback button in UI
        self.isPlayable = isPlayable
        # whether to offer item expansion in UI
        self.isLeaf = isLeaf

    def __str__(self) -> str:
        return super().__str__() \
               + "; nodeID: " + str(self.nodeID) \
               + "; label: " + self.label \
               + "; isPlayable: " + str(self.isPlayable) \
               + "; isLeaf: " + str(self.isLeaf)


class NodeStruct:
    def __init__(self,
                 # this node
                 node: 'NodeItem',
                 # ID of parent item. NON_EXISTING_NODE_ID => root item
                 parentID: NodeID,
                 # list of children items
                 children: List['NodeItem'],
                 # the 'children' list starts at fromIndex of all children collection - 0-based
                 fromIndex: int,
                 # total number of all children of the node
                 total: int
                 ):
        self.node = node
        self.parentID = parentID
        self.children = children
        self.fromIndex = fromIndex
        self.total = total

    def __str__(self) -> str:
        return super().__str__() \
               + "; node: " + str(self.node) \
               + "; parentID: " + str(self.parentID) \
               + "; children: " + '\n'.join(str(p) for p in self.children) \
               + "; fromIndex: " + str(self.fromIndex) \
               + "; total: " + str(self.total)
