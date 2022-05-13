from dataclasses import dataclass
from typing import Any, Dict, Optional

from steamship.base import Client


@dataclass
class ExportPluginInput:
    pluginInstance: str = None
    id: str = None
    handle: str = None
    type: str = None
    filename: str = None
    query: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(
            d: Any = None, client: Client = None
    ) -> "Optional[ExportPluginInput]":
        if d is None:
            return None

        return ExportPluginInput(
            pluginInstance=d.get("pluginInstance", None),
            id=d.get("id", None),
            handle=d.get("id", None),
            type=d.get("type", None),
            filename=d.get("filename", None),
            query=d.get("query", None),
        )

    def to_dict(self) -> Dict:
        return dict(
            pluginInstance=self.pluginInstance,
            id=self.id,
            handle=self.handle,
            type=self.type,
            filename=self.filename,
            query=self.query,
        )
