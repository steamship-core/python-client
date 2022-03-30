import base64
import logging
from dataclasses import dataclass
from typing import Dict, Any

from steamship.base import Client
from steamship.data.file import File

@dataclass
class ClientsideConvertRequest:
    type: str = None
    pluginInstance: str = None
    id: str = None
    handle: str = None
    name: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ClientsideConvertRequest":
        return ClientsideConvertRequest(
            type=d.get('type', None),
            pluginInstance=d.get('pluginInstance', None),
            id=d.get('id', None),
            handle=d.get('handle', None),
            name=d.get('name', None)
        )






