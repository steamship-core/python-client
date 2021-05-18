from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponse
from nludb.types.search import Hit
@dataclass
class IndexCreateRequest(NludbRequest):
  name: str
  model: str
  upsert: bool = True
  externalId: str = None
  externalType: str = None
  metadata: any = None

@dataclass
class IndexCreateResponse(NludbResponse):
  id: str

@dataclass
class IndexInsertRequest(NludbRequest):
  indexId: str
  value: str
  externalId: str = None
  externalType: str = None
  metadata: any = None
  reindex: bool = True

@dataclass
class IndexItemId(NludbResponse):
  indexId: str = None
  id: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "IndexItemId":
    return IndexItemId(
      indexId = d.get('indexId', None),
      id = d.get('id', None)
    )

@dataclass
class IndexInsertResponse(NludbResponse):
  itemIds: List[IndexItemId] = None

  @staticmethod
  def safely_from_dict(d: any) -> "IndexInsertResponse":
    return IndexInsertResponse(
      itemIds = [IndexItemId.safely_from_dict(x) for x in d.get('itemIds', [])]
    )

@dataclass
class IndexEmbedRequest(NludbRequest):
  indexId: str

@dataclass
class IndexEmbedResponse(NludbResponse):
  indexId: str

  @staticmethod
  def safely_from_dict(d: any) -> "IndexEmbedResponse":
    return IndexEmbedResponse(
      indexId = d.get('indexId', None)
    )


@dataclass
class IndexDeleteRequest(NludbRequest):
  indexId: str

@dataclass
class IndexDeleteResponse(NludbResponse):
  indexId: str

  @staticmethod
  def safely_from_dict(d: any) -> "IndexDeleteResponse":
    return IndexDeleteResponse(
      indexId = d.get('indexId', None)
    )

@dataclass
class IndexSearchRequest(NludbRequest):
  indexId: str
  query: str
  k: int = 1
  includeMetadata: bool = False

@dataclass
class IndexSearchResponse(NludbResponse):
  hits: List[Hit] = None

  @staticmethod
  def safely_from_dict(d: any) -> "IndexSearchResponse":
    hits = [Hit.safely_from_dict(h) for h in d.get("hits", [])]
    return IndexSearchResponse(
      hits=hits
    )
