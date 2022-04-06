from dataclasses import dataclass
from typing import List
from steamship.base import Client

@dataclass
class EmbeddedItemsPluginOutput:
    embeddings: List[List[float]]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbeddedItemPluginOutput":
        return EmbeddedItemsPluginOutput(
            embeddings=d.get('embeddings', None),
        )

    def to_dict(self) -> dict:
        return dict(
            embeddings=self.embeddings
        )
