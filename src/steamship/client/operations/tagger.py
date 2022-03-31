import json
from dataclasses import dataclass, asdict
from typing import List

from steamship import File
from steamship.base import Client


@dataclass
class TagRequest:
    type: str = None
    id: str = None
    name: str = None
    handle: str = None
    pluginInstance: str = None
    file: File.CreateRequest = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "TagRequest":

        return TagRequest(
            type = d.get('type', None),
            id = d.get('id', None),
            name = d.get('name', None),
            handle = d.get('handle', None),
            pluginInstance= d.get('pluginInstance', None),
            file= File.CreateRequest.from_dict(d.get('file', {}))
        )

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class TagResponse:
    file: File = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "TagResponse":
        return TagResponse(
            file= File.from_dict(d.get('file', {}))
        )

    def to_dict(self) -> dict:
        return asdict(self)
