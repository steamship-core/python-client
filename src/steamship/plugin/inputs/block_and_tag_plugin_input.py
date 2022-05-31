from __future__ import annotations

from pydantic import BaseModel

from steamship import File
from steamship.base import Client


class BlockAndTagPluginInput(BaseModel):
    file: File = None
