from dataclasses import dataclass
from typing import Any, Dict, List

from steamship.base import Client


@dataclass
class EmbedRequest:
    docs: List[str]
    pluginInstance: str
    metadata: Dict = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "EmbedRequest":
        # TODO (enias): Review these _: Client lines
        return EmbedRequest(
            docs=d.get("docs"),
            pluginInstance=d.get("pluginInstance"),
            metadata=d.get("metadata", {}),
        )
