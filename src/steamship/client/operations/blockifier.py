from dataclasses import dataclass
from typing import Any

from steamship.base import Client


@dataclass
class BlockifyRequest:
    type: str = None
    pluginInstance: str = None
    id: str = None
    handle: str = None
    name: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "BlockifyRequest":
        return BlockifyRequest(
            type=d.get("type"),
            pluginInstance=d.get("pluginInstance"),
            id=d.get("id"),
            handle=d.get("handle"),
            name=d.get("name"),
        )
