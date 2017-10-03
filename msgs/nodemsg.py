from typing import List, NewType, Optional

from groupid import GroupID
from moduleid import ModuleID
from msgid import MsgID
from msgs.message import Message

NodeID = NewType('NodeID', int)

NON_EXISTING_NODE_ID = 0


def isBookmark(nodeID: NodeID) -> bool:
    """
    nodeIDs of bookmark nodes are < 0
    """
    return nodeID < 0


class NodeMsg(Message):
    """
    Msg with node information
    """

    def __init__(self, nodeStruct: 'NodeStruct', fromID: ModuleID, forID=ModuleID.ANY, groupID=GroupID.ANY):
        super().__init__(fromID=fromID, typeID=MsgID.NODE_INFO, forID=forID, groupID=groupID)
        self.nodeStruct = nodeStruct

    def __str__(self) -> str:
        return super().__str__() + "; " + str(self.nodeStruct)


class NodeItem:
    """
    Item for the Node, data container between Source and UI
    """

    def __init__(self, nodeID: NodeID, label: str, isPlayable: bool, isLeaf: bool, bookmarkID: Optional[NodeID]):
        # fixed ID tracked by the source. Used to streamline the messages
        self.nodeID = nodeID
        # shown in the UI
        self.label = label
        # whether to offer playback button in UI
        self.isPlayable = isPlayable
        # whether to offer item expansion in UI
        self.isLeaf = isLeaf
        # ID of corresponding bookmark node, optional
        self.bookmarkID = bookmarkID

    def __str__(self) -> str:
        return super().__str__() \
               + "; nodeID: " + str(self.nodeID) \
               + "; label: " + self.label \
               + "; isPlayable: " + str(self.isPlayable) \
               + "; isLeaf: " + str(self.isLeaf) \
               + "; bookmakrID: " + str(self.bookmarkID)


class NodeStruct:
    def __init__(self,
                 # this node
                 node: 'NodeItem',
                 # root node
                 rootNode: 'NodeItem',
                 # index of node within its siblings
                 totalParents: int,
                 # ID of parent item. NON_EXISTING_NODE_ID => root item
                 parentID: NodeID,
                 # list of children items
                 children: List['NodeItem'],
                 # the 'children' list starts at fromIndex of all children collection - 0-based
                 fromChildIndex: int,
                 # total number of all children of the node
                 totalChildren: int
                 ):
        self.node = node
        self.rootNode = rootNode
        self.totalParents = totalParents
        self.parentID = parentID
        self.children = children
        self.fromChildIndex = fromChildIndex
        self.totalChildren = totalChildren

    def __str__(self) -> str:
        return super().__str__() \
               + "; node: " + str(self.node) \
               + "; rootNode: " + str(self.rootNode) \
               + "; totalParents: " + str(self.totalParents) \
               + "; parentID: " + str(self.parentID) \
               + "; children: " + '\n'.join(str(p) for p in self.children) \
               + "; fromChildIndex: " + str(self.fromChildIndex) \
               + "; totalChildren: " + str(self.totalChildren)
