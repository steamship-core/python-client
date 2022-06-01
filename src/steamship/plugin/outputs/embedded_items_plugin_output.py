from __future__ import annotations

from typing import List

from pydantic import BaseModel


class EmbeddedItemsPluginOutput(BaseModel):
    embeddings: List[List[float]]
