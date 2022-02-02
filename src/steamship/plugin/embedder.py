from abc import ABC
from dataclasses import dataclass
from typing import Dict, List, Any

from steamship.base import Client
from steamship.plugin.service import PluginService, PluginRequest


@dataclass
class EmbedRequest:
    docs: List[str]
    model: str
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbedRequest":
        return EmbedRequest(
            docs=d.get('docs', None),
            model=d.get('model', None),
            metadata=d.get('metadata', {})
        )


@dataclass
class EmbedResponse:
    embeddings: List[List[float]]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbedResponse":
        return EmbedResponse(
            embeddings=d.get('embeddings', None),
        )

    def to_dict(self) -> dict:
        return dict(
            embeddings=self.embeddings
        )

    def to_pandas(self) -> Any:
        import pandas as pd
        return pd.DataFrame(self.embeddings)

class Embedder(PluginService[EmbedRequest, EmbedResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[EmbedRequest]:
        return EmbedRequest.from_dict(d, client=client)
