from __future__ import annotations

from typing import Any

from steamship import File
from steamship.base import Client, Request


class TagRequest(Request):
    type: str = None
    id: str = None
    name: str = None
    handle: str = None
    pluginInstance: str = None
    file: File.CreateRequest = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> TagRequest:
        return TagRequest(
            type=d.get("type"),
            id=d.get("id"),
            name=d.get("name"),
            handle=d.get("handle"),
            pluginInstance=d.get("pluginInstance"),
            file=File.CreateRequest.from_dict(d.get("file", {})),
        )

    def to_dict(self) -> dict:
        return self.dict()


class TagResponse(Request):
    file: File = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> TagResponse:
        return TagResponse(file=File.from_dict(d.get("file", {})))

    def to_dict(self) -> dict:
        return self.dict()
