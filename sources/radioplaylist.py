#!/usr/bin/python3

import logging
import os
from typing import List

from lxml import etree
from treelib import Tree

from sources.nodeidprovider import NodeIDProvider

PLAYLIST_FILENAME = "radios.xml"


class RadioPlaylist(NodeIDProvider):
    """
    Loading radio groups and items from PLAYLIST_FILENAME
    """

    def __init__(self, filename):
        NodeIDProvider.__init__(self)
        self.log = logging.getLogger('RadioPlaylist')
        if os.access(filename, os.R_OK):  # if can read, then use.
            self._filename = filename
        else:  # if can't read, give error.
            raise Exception('Radios file not found: ' + filename)

    def loadTreeFromFile(self) -> Tree:
        self.log.info('Loading radios file: %s', self._filename)
        self._xmlRoot = etree.parse(self._filename).getroot()
        self.log.debug('Bookmarks file loaded with success')

        tree = Tree()
        rootID = self._getNextID()
        tree.create_node(identifier=rootID, parent=None, data=GroupItem("Radios"))
        for groupName in self._listGroupNames():
            groupID = self._getNextID()
            tree.create_node(identifier=groupID, parent=rootID, data=GroupItem(groupName))
            for radioName in self._listRadioNamesInGroup(groupName):
                radioID = self._getNextID()
                tree.create_node(identifier=radioID, parent=groupID,
                                 data=RadioItem(radioName, self._getRadioUrl(radioName)))
        return tree

    def _listGroupNames(self) -> List[str]:
        return self._xmlRoot.xpath("//group/@name")

    def _listRadioNamesInGroup(self, group: str) -> List[str]:
        return self._xmlRoot.xpath("//group[@name=$var]/bookmark/@name", var=group)

    def _getRadioUrl(self, radioName: str) -> str:
        result = self._xmlRoot.xpath("//bookmark[@name=$var]/@url", var=radioName)
        if len(result) >= 1:
            return result[0]


class GroupItem:
    def __init__(self, name: str) -> None:
        self.name = name


class RadioItem:
    def __init__(self, name: str, url: str) -> None:
        self.url = url
        self.name = name


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
    playlist = RadioPlaylist(PLAYLIST_FILENAME)
    tree = playlist.loadTreeFromFile()
    tree.show(idhidden=False, line_type='ascii', data_property="name")
