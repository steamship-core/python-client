from __future__ import annotations

from typing import List

from steamship.plugin.outputs.plugin_output import PluginOutput


class EmbeddedItemsPluginOutput(PluginOutput):
    embeddings: List[List[float]]
