from dataclasses import dataclass
from typing import List, Dict

from steamship.base import Client, Request
from steamship.data.search import Hit

@dataclass
class EmbedRequest:
    docs: List[str]
    plugin: str
    metadata: Dict = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbedRequest":
        return EmbedRequest(
            docs=d.get('docs', None),
            plugin=d.get('plugin', None),
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


@dataclass
class EmbedAndSearchRequest(Request):
    query: str
    docs: List[str]
    plugin: str
    k: int = 1


@dataclass
class EmbedAndSearchResponse(Request):
    hits: List[Hit] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbedAndSearchResponse":
        hits = [Hit.from_dict(h) for h in (d.get("hits", []) or [])]
        return EmbedAndSearchResponse(
            hits=hits
        )
