#!/usr/bin/python3

import logging
import os
from typing import Optional

from lxml import etree
from lxml.etree import Element
from treelib import Tree

from msgs.nodemsg import NodeID
from sources.nodeidprovider import NodeIDProvider

PLAYLIST_FILENAME = "radios.xml"


class RadioPlaylist():
    """
    Loading radio groups and items from PLAYLIST_FILENAME
    """

    def __init__(self, filename):
        self._idProvider = NodeIDProvider()
        self.log = logging.getLogger('RadioPlaylist')
        if os.access(filename, os.R_OK):  # if can read, then use.
            self._filename = filename
        else:  # if can't read, give error.
            raise Exception('Radios file not found: ' + filename)

    def loadTreeFromFile(self) -> Tree:
        self.log.info('Loading radios file: %s', self._filename)
        self._xmlRoot = etree.parse(self._filename).getroot()
        self.log.debug('File %s loaded with success', self._filename)

        tree = Tree()
        rootID = self._idProvider.getNextID()
        tree.create_node(identifier=rootID, parent=None, data=GroupItem("Radios"))
        for childNode in self._xmlRoot:
            self._parseNode(childNode, tree, rootID)
        return tree

    def _parseNode(self, node: Element, tree: Tree, parentID: Optional[NodeID]):
        nodeID = self._idProvider.getNextID()
        if node.tag == "group":
            groupName = node.attrib["name"]
            tree.create_node(identifier=nodeID, parent=parentID, data=GroupItem(groupName))
            for childNode in node:
                self._parseNode(childNode, tree, nodeID)
        elif node.tag == "bookmark":
            radioName = node.attrib["name"]
            url = node.attrib["url"]
            tree.create_node(identifier=nodeID, parent=parentID,
                             data=RadioItem(radioName, url))


class GroupItem:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return super().__str__() \
               + "; name: " + self.name


class RadioItem:
    def __init__(self, name: str, url: str) -> None:
        self.url = url
        self.name = name

    def __str__(self) -> str:
        return super().__str__() \
               + "; name: " + self.name \
               + "; url: " + self.url


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
    playlist = RadioPlaylist(PLAYLIST_FILENAME)
    tree = playlist.loadTreeFromFile()
    tree.show(idhidden=False, line_type='ascii', data_property="name")
