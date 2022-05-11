from dataclasses import dataclass
from typing import Any, Dict, Optional

from pydantic import BaseModel

from steamship import File
from steamship.base import Client


class BlockAndTagPluginInput(BaseModel):
    file: File = None

    @staticmethod
    def from_dict(
        d: Any = None, client: Client = None
    ) -> "Optional[BlockAndTagPluginInput]":
        if d is None:
            return None

        return BlockAndTagPluginInput(
            file=File.from_dict(d.get("file", None), client=client)
        )
