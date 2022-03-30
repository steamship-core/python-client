from dataclasses import dataclass
from typing import List, Dict
from steamship.base import Client


@dataclass
class EmbedRequest:
    docs: List[str]
    plugin: str
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbedRequest":
        return EmbedRequest(
            docs=d.get('docs', None),
            plugin=d.get('plugin', None),
            metadata=d.get('metadata', {})
        )