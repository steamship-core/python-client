from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict

from steamship.plugin.base import Plugin, PluginRequest, PluginResponse


@dataclass
class ImportRequest:
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any) -> "ImportRequest":
        return ImportRequest(
            metadata=d.get('metadata', {})
        )


@dataclass
class ImportResponse:
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any) -> "ImportRequest":
        return ImportRequest(
            metadata=d.get('metadata', {})
        )


class Importer(Plugin):
    @abstractmethod
    def _run(self, request: PluginRequest[ImportRequest]) -> PluginResponse[ImportResponse]:
        pass
