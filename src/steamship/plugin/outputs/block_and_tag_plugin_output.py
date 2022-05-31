from __future__ import annotations

from pydantic import BaseModel

from steamship.base import Client
from steamship.data.file import File


class BlockAndTagPluginOutput(BaseModel):
    file: File.CreateRequest = None
