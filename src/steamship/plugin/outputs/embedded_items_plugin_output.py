from dataclasses import dataclass
from typing import Any, List

from steamship.base import Client


@dataclass
class EmbeddedItemsPluginOutput:
    embeddings: List[List[float]]

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "EmbeddedItemsPluginOutput":
        return EmbeddedItemsPluginOutput(
            embeddings=d.get("embeddings", None),
        )

    def to_dict(self) -> dict:
        return dict(embeddings=self.embeddings)
