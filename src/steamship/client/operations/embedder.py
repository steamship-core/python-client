from dataclasses import dataclass
from typing import List, Dict
from steamship.base import Client


@dataclass
class EmbedRequest:
    docs: List[str]
    pluginInstance: str
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbedRequest":
        return EmbedRequest(
            docs=d.get('docs', None),
            pluginInstance=d.get('pluginInstance', None),
            metadata=d.get('metadata', {})
        )