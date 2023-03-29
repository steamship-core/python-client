from __future__ import annotations

from typing import List

from steamship.data.file import Block
from steamship.plugin.outputs.plugin_output import PluginOutput


class RawBlockAndTagPluginOutput(PluginOutput):
    blocks: List[Block]
