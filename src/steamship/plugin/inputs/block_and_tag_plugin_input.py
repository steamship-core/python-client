from __future__ import annotations

from pydantic import BaseModel

from steamship import File


class BlockAndTagPluginInput(BaseModel):
    file: File = None
