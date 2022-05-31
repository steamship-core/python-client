from __future__ import annotations

from typing import List

from pydantic import BaseModel

from steamship.base import Client


class EmbeddedItemsPluginOutput(BaseModel):
    embeddings: List[List[float]]
