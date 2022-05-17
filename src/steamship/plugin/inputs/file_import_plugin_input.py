from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel

from steamship.base import Client


class FileImportPluginInput(BaseModel):
    value: str = None
    data: str = None
    url: str = None
    pluginInstance: str = None
    mimeType: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(
        d: Any = None, client: Client = None
    ) -> Optional[FileImportPluginInput]:
        if d is None:
            return None

        return FileImportPluginInput(
            value=d.get("value"),
            data=d.get("data"),
            url=d.get("url"),
            pluginInstance=d.get("pluginInstance"),
            mimeType=d.get("mimeType"),
        )

    def to_dict(self) -> Dict:
        # TODO (enias): Debug why we reference a non-existent variable file
        raise NotImplementedError()
