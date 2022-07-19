from __future__ import annotations

from typing import List

from steamship.base.configuration import CamelModel


class EmbeddedItemsPluginOutput(CamelModel):
    embeddings: List[List[float]]
