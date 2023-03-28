from __future__ import annotations

from typing import List

from steamship.base.model import CamelModel
from steamship.data.file import Block


class RawBlockAndTagPluginOutput(CamelModel):
    blocks: List[Block]
