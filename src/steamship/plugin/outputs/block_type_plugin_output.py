from __future__ import annotations

from typing import List

from steamship.plugin.outputs.plugin_output import PluginOutput


class BlockTypePluginOutput(PluginOutput):
    block_types_to_create: List[str]
