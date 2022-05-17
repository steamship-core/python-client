from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel

from steamship.base import Client
from steamship.data.file import File


class BlockAndTagPluginOutput(BaseModel):
    file: File.CreateRequest = None

    @staticmethod
    def from_dict(
        d: Any = None, client: Client = None
    ) -> Optional[BlockAndTagPluginOutput]:
        if d is None:
            return None

        return BlockAndTagPluginOutput(
            file=File.CreateRequest.from_dict(d.get("file"), client=client)
        )

    def to_dict(self) -> Dict:
        if self.file is None:
            return {}
        return {"file": self.file.to_dict()}
