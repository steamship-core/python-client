from dataclasses import dataclass
from typing import Dict

from steamship.base import Client


@dataclass
class FileImportPluginInput:
    value: str = None
    data: str = None
    url: str = None
    pluginInstance: str = None
    mimeType: str = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "FileImportPluginInput":
        if d is None:
            return None

        return FileImportPluginInput(
            value = d.get('value', None),
            data = d.get('data', None),
            url = d.get('url', None),
            pluginInstance = d.get('pluginInstance', None),
            mimeType = d.get('mimeType', None),
        )

    def to_dict(self) -> Dict:
        if self.file is None:
            return dict()
        return dict(file=self.file.to_dict())
