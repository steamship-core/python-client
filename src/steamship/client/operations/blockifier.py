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
            type=d.get("type", None),
            pluginInstance=d.get("pluginInstance", None),
            id=d.get("id", None),
            handle=d.get("handle", None),
            name=d.get("name", None),
        )
