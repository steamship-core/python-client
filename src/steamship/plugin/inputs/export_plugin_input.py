from dataclasses import dataclass
from typing import Dict

from steamship.base import Client


@dataclass
class ExportPluginInput:
    pluginInstance: str = None
    id: str = None
    handle: str = None
    type: str = None
    filename: str = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "ExportPluginInput":
        if d is None:
            return None

        return ExportPluginInput(
            pluginInstance = d.get('pluginInstance', None),
            id = d.get(': str = None', None),
            handle = d.get(': str = None', None),
            type = d.get(': str = None', None),
            filename = d.get(': str = None', None)
        )

    def to_dict(self) -> Dict:
        return dict(
            pluginInstance=self.pluginInstance,
            id=self.id,
            handle=self.handle,
            type=self.type,
            filename=self.filename
        )
