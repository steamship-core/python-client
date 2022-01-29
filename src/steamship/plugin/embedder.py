from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, List

from steamship.plugin.service import PluginService, PluginRequest, PluginResponse


@dataclass
class EmbedRequest:
    docs: List[str]
    model: str
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any) -> "EmbedRequest":
        return EmbedRequest(
            docs=d.get('docs', None),
            model=d.get('model', None),
            metadata=d.get('metadata', {})
        )


@dataclass
class EmbedResponse:
    embeddings: List[List[float]]

    @staticmethod
    def from_dict(d: any) -> "EmbedResponse":
        return EmbedResponse(
            embeddings=d.get('embeddings', None),
        )

    def to_dict(self) -> dict:
        return dict(
            embeddings=self.embeddings
        )


class Embedder(PluginService):
    @abstractmethod
    def _run(self, request: PluginRequest[EmbedRequest]) -> PluginResponse[EmbedResponse]:
        pass
