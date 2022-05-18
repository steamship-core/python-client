from dataclasses import dataclass
from typing import Any, Dict, Optional

from steamship.base import Client


@dataclass
class ExportPluginInput:
    plugin_instance: str = None
    id: str = None
    handle: str = None
    type: str = None
    filename: str = None
    query: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any = None, client: Client = None) -> "Optional[ExportPluginInput]":
        if d is None:
            return None

        return ExportPluginInput(
            plugin_instance=d.get("pluginInstance"),
            id=d.get("id"),
            handle=d.get("id"),
            type=d.get("type"),
            filename=d.get("filename"),
            query=d.get("query"),
        )

    def to_dict(self) -> Dict:
        return dict(
            pluginInstance=self.plugin_instance,
            id=self.id,
            handle=self.handle,
            type=self.type,
            filename=self.filename,
            query=self.query,
        )
