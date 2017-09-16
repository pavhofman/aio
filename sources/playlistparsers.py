from __future__ import absolute_import, unicode_literals

import configparser
import io
import urllib
from typing import List

try:
    import xml.etree.cElementTree as elementtree
except ImportError:
    import xml.etree.ElementTree as elementtree

"""
Parsers for extracting URLs from various playlist formats
Inspired by mopidy https://github.com/mopidy/mopidy/blob/develop/mopidy/internal/playlists.py
"""


def parse(data: bytes):
    handlers = {
        detect_extm3u_header: parse_extm3u,
        detect_pls_header: parse_pls,
        detect_asx_header: parse_asx,
        detect_xspf_header: parse_xspf,
    }
    for detector, parser in handlers.items():
        if detector(data):
            return list(parser(data))
    return parse_urilist(data)  # Fallback


def detect_extm3u_header(data):
    return data[0:7].upper() == b'#EXTM3U'


def detect_pls_header(data):
    return data[0:10].lower() == b'[playlist]'


def detect_xspf_header(data):
    data = data[0:150]
    if b'xspf' not in data.lower():
        return False

    try:
        data = io.BytesIO(data)
        for event, element in elementtree.iterparse(data, events=(b'start',)):
            return element.tag.lower() == '{http://xspf.org/ns/0/}playlist'
    except elementtree.ParseError:
        pass
    return False


def detect_asx_header(data: bytes):
    data = data[0:50]
    if b'asx' not in data.lower():
        return False

    try:
        bytesIO = io.BytesIO(data)
        for event, element in elementtree.iterparse(bytesIO, events=(b'start',)):
            return element.tag.lower() == 'asx'
    except elementtree.ParseError:
        pass
    return False


def parse_extm3u(data: bytes) -> List[bytes]:
    found_header = False
    for line in data.splitlines():
        if found_header or line.startswith(b'#EXTM3U'):
            found_header = True
        else:
            continue
        if not line.startswith(b'#') and line.strip():
            yield line.strip()


def parse_pls(data: bytes):
    # TODO: convert non URIs to file URIs.
    try:
        cp = configparser.ConfigParser()
        cp.read_string(data.decode("utf-8"))
    except configparser.Error:
        return

    for section in cp.sections():
        if section.lower() != 'playlist':
            continue
        for i in range(cp.getint(section, 'numberofentries', fallback=0)):
            yield cp.get(section, 'file%d' % (i + 1))


def parse_xspf(data: bytes):
    try:
        # Last element will be root.
        element = None
        for event, element in elementtree.iterparse(io.BytesIO(data)):
            element.tag = element.tag.lower()  # normalize
        if element is not None:
            ns = 'http://xspf.org/ns/0/'
            for track in element.iterfind('{%s}tracklist/{%s}track' % (ns, ns)):
                yield track.findtext('{%s}location' % ns)
    except elementtree.ParseError:
        return


def parse_asx(data):
    try:
        # Last element will be root.
        element = None
        for event, element in elementtree.iterparse(io.BytesIO(data)):
            element.tag = element.tag.lower()  # normalize

        if element is not None:
            for ref in element.findall('entry/ref[@href]'):
                yield ref.get('href', '').strip()

            for entry in element.findall('entry[@href]'):
                yield entry.get('href', '').strip()
    except elementtree.ParseError:
        return


def parse_urilist(data: bytes) -> List[bytes]:
    result = []
    for line in data.splitlines():
        if not line.strip() or line.startswith(b'#'):
            continue
        try:
            check_uri(line)
        except ValueError:
            return []
        result.append(line)
    return result


def check_uri(arg, msg='Expected a valid URI, not {arg!r}'):
    # noinspection PyUnresolvedReferences
    if not isinstance(arg, (str,)):
        raise ValidationError(msg.format(arg=arg))
    elif urllib.parse.urlparse(arg).scheme == '':
        raise ValidationError(msg.format(arg=arg))


class ValidationError(ValueError):
    pass
