from enum import Enum
from typing import Dict, Any, List

from steamship import Tag


class FileType(str, Enum):
    YOUTUBE = "YOUTUBE"
    PDF = "PDF"
    WEB = "WEB"
    TEXT = "TEXT"


def metadata_to_tags(metadata: Dict[str, Any]):
    return [Tag(kind=k, name=v) for k, v in metadata.items()]