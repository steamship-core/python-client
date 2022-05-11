from dataclasses import dataclass
from typing import Any, Dict, Optional

from steamship.base import Client


@dataclass
class FileImportPluginInput:
    value: str = None
    data: str = None
    url: str = None
    pluginInstance: str = None
    mimeType: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(
        d: Any = None, client: Client = None
    ) -> "Optional[FileImportPluginInput]":
        if d is None:
            return None

        return FileImportPluginInput(
            value=d.get("value", None),
            data=d.get("data", None),
            url=d.get("url", None),
            pluginInstance=d.get("pluginInstance", None),
            mimeType=d.get("mimeType", None),
        )

    def to_dict(self) -> Dict:
        # TODO (enias): Debug why we reference a non-existent variable file
        raise NotImplementedError()
