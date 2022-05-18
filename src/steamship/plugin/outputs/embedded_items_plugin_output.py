from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel

from steamship.base import Client


class EmbeddedItemsPluginOutput(BaseModel):
    embeddings: List[List[float]]

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> EmbeddedItemsPluginOutput:
        return EmbeddedItemsPluginOutput(
            embeddings=d.get("embeddings"),
        )

    def to_dict(self) -> dict:
        return dict(embeddings=self.embeddings)
