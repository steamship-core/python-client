from __future__ import annotations

from steamship import File
from steamship.base.configuration import CamelModel


class BlockAndTagPluginInput(CamelModel):
    file: File = None
