import json
from typing import Dict, List, Optional

from unidecode import unidecode

from metadata import Metadata


class MetadataParser:
    """
    Parser for metadata from MPV - parsing to JSON for MsgID.METADATA_INFO msg
    """

    def __init__(self, rules: Dict[Metadata, List[str]]) -> None:
        self.__rulesDict = rules

    def parseToJsonStr(self, metadata: dict) -> Optional[str]:
        """
        :return: json string or None if no matching non-empty metadata found
        """
        jsonDict = {}
        for md, possibleKeys in self.__rulesDict.items():
            for key in possibleKeys:
                if key in metadata:
                    value = metadata.get(key)
                    if len(value) > 0:
                        jsonDict[md.value] = unidecode(value)
                        # found first value, skipping other possible keys for the metadata
                        break

        if len(jsonDict) > 0:
            return json.dumps(jsonDict)
        else:
            return None
