from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData
from nludb.types.search import Hit

@dataclass
class EmbedRequest(NludbRequest):
  texts: List[str]
  model: str

@dataclass
class EmbedResponse(NludbResponseData):
  embeddings: List[List[float]]

  @staticmethod
  def safely_from_dict(d: any) -> "EmbedResponse":
    return EmbedResponse(
      embeddings = d.get('embeddings', None),
    )

@dataclass
class EmbedAndSearchRequest(NludbRequest):
  query: str
  docs: List[str]
  model: str
  k: int = 1

@dataclass
class EmbedAndSearchResponse(NludbRequest):
  hits: List[Hit] = None

  @staticmethod
  def safely_from_dict(d: any) -> "EmbedAndSearchResponse":
    hits = [Hit.safely_from_dict(h) for h in (d.get("hits", []) or [])]
    return EmbedAndSearchResponse(
      hits=hits
    )

