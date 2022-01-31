from dataclasses import dataclass
from typing import List

from steamship.base import Client, Request
from steamship.data.search import Hit


@dataclass
class EmbedAndSearchRequest(Request):
    query: str
    docs: List[str]
    model: str
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
