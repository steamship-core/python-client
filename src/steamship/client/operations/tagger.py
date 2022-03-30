import json
from dataclasses import dataclass, asdict
from typing import List

from steamship.base import Client


@dataclass
class TagRequest:
    type: str = None
    id: str = None
    name: str = None
    handle: str = None
    docs: List[str] = None
    blockIds: List[str] = None
    pluginInstance: str = None
    includeTokens: bool = True
    includeParseData: bool = True
    includeEntities: bool = False
    metadata: any = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "TagRequest":
        includeTokens = d.get("includeTokens", True)
        if includeTokens is None:
            includeTokens = True

        includeParseData = d.get("includeParseData", True)
        if includeParseData is None:
            includeParseData = True

        includeEntities = d.get("includeEntities", True)
        if includeEntities is None:
            includeEntities = True

        metadata = d.get("metadata", None)
        if metadata is not None:
            try:
                metadata = json.loads(metadata)
            except:
                pass

        return TagRequest(
            docs=(d.get("docs", []) or []),
            blockIds=(d.get("blockIds", []) or []),
            plugin=d.get("plugin", None),
            includeTokens=includeTokens,
            includeParseData=includeParseData,
            includeEntities=includeEntities,
            metadata=metadata
        )

    def to_dict(self) -> dict:
        return asdict(self)
