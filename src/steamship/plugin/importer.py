from abc import ABC
from dataclasses import dataclass
from typing import Dict

from steamship.base import Client
from steamship.plugin.service import PluginService, PluginRequest


@dataclass
class ImportRequest:
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ImportRequest":
        return ImportRequest(
            metadata=d.get('metadata', {})
        )


@dataclass
class ImportResponse:
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ImportRequest":
        return ImportRequest(
            metadata=d.get('metadata', {})
        )


class Importer(PluginService[ImportRequest, ImportResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[ImportRequest]:
        return ImportRequest.from_dict(d, client=client)
