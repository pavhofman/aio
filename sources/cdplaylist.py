#!/usr/bin/python3

import logging
from typing import Optional, Dict, Tuple

import discid
import musicbrainzngs
from discid import Disc, Track
from treelib import Tree

import config
from sources.nodeidprovider import NodeIDProvider

DEFAULT_CD_NAME = "CD"

musicbrainzngs.set_useragent(
    "plabs-aio",
    "0.1",
    "https://github.com/pavhofman/aio",
)


class CDPlaylist:
    """
    Loading CD tracks from medium. Trying to load names/tracks from MusicBrainz
    """

    def __init__(self):
        self._idProvider = NodeIDProvider()
        self.log = logging.getLogger('CDPlaylist')

    def loadTreeFromCD(self) -> Tree:
        self.log.info('Loading CD')
        disc = discid.read(config.DEV_CDROM)
        discName, trackNamesByPosition = self.__readNamesFromMB(disc)

        tree = Tree()
        rootID = self._idProvider.getNextID()
        tree.create_node(identifier=rootID, parent=None, data=RootItem(discName))
        startsAtSecs = 0
        for track in disc.tracks:  # type: Track
            nodeID = self._idProvider.getNextID()
            position = track.number
            trackName = self.__getTrackName(position, trackNamesByPosition)
            lengthInSecs = track.seconds
            tree.create_node(identifier=nodeID, parent=rootID,
                             data=TrackItem(trackName, position, lengthInSecs, startsAtSecs))
            # startAtSecs for next track
            startsAtSecs += lengthInSecs
        return tree

    def __readNamesFromMB(self, disc: Disc) -> Tuple[str, Dict[int, str]]:
        """
        Reads name of CD and individual tracks from musicbrainz
        Track names are stored in dictionary trackID -> trackName
        If not found, returns default CD name and empty dictionary
        :param disc:
        :return:
        """
        discID = disc.id  # type: str
        try:
            result = musicbrainzngs.get_releases_by_discid(discID, includes=["labels", "recordings"])
            if result.get('disc'):
                for release in result['disc']['release-list']:
                    cdName = release['title']  # type:Optional[str]
                    trackNamesByPosition = {}
                    if release.get('medium-list'):
                        media = release['medium-list']
                        for medium in media:
                            if self.__mediumHasDiscID(medium, discID):
                                for track in medium['track-list']:
                                    recording = track['recording']
                                    trackNamesByPosition[int(track['position'])] = recording['title']
                                if len(trackNamesByPosition) > 0:
                                    # found some tracks
                                    if len(media) > 1:
                                        # multiple media in release - adding medium position to CD name
                                        cdName += ", CD " + medium['position']
                                    return cdName, trackNamesByPosition
        except musicbrainzngs.ResponseError as err:
            if err.cause.code == 404:
                logging.debug("disc ID %s not found" % discID)
            else:
                logging.error("received bad response from the MB server")
        return DEFAULT_CD_NAME, {}

    def __mediumHasDiscID(self, medium: Dict, discID: str) -> bool:
        if medium.get('disc-list'):
            for disc in medium['disc-list']:  # type: Dict
                if disc['id'] == discID:
                    return True
        return False

    @staticmethod
    def __getTrackName(position: int, trackNamesByPosition: Dict[int, str]) -> str:
        if position in trackNamesByPosition.keys():
            return trackNamesByPosition[position]
        else:
            return "Track " + str(position)


class RootItem:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return super().__str__() \
               + "; name: " + self.name


class TrackItem:
    def __init__(self, name: str, trackID: int, lengthSecs: int, startsAtSecs: int) -> None:
        self.name = name
        # 1 ... num tracks
        self.trackID = trackID
        self.lengthSecs = lengthSecs
        # track starts secsFromStart seconds from beginning of CD
        self.startsAtSecs = startsAtSecs

    def __str__(self) -> str:
        return super().__str__() \
               + "; name: " + self.name \
               + "; trackID: " + str(self.trackID)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
    playlist = CDPlaylist()
    tree = playlist.loadTreeFromCD()
    tree.show(idhidden=False, line_type='ascii', data_property="name")
