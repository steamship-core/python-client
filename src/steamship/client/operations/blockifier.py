from __future__ import annotations

from typing import Any

from steamship.base import Client, Request


class BlockifyRequest(Request):
    type: str = None
    pluginInstance: str = None
    id: str = None
    handle: str = None
    name: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> BlockifyRequest:
        return BlockifyRequest(
            type=d.get("type"),
            pluginInstance=d.get("pluginInstance"),
            id=d.get("id"),
            handle=d.get("handle"),
            name=d.get("name"),
        )
