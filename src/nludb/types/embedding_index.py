from typing import List
import json
from dataclasses import dataclass
from nludb.types.base import Request, Model, metadata_to_str
from nludb.types.search import Hit
from nludb.base.base import ApiBase 

@dataclass
class IndexCreateRequest(Request):
  handle: str = None
  name: str = None
  model: str = None
  upsert: bool = True
  externalId: str = None
  externalType: str = None
  metadata: any = None


@dataclass
class IndexItem:
  itemId: str = None
  indexId: str = None
  fileId: str = None
  blockId: str = None
  spanId: str = None
  value: str = None
  externalId: str = None
  externalType: str = None
  metadata: any = None
  embedding: List[float] = None

  def clone_for_insert(self) -> "IndexItem":
    """Produces a clone with a string representation of the metadata"""
    ret = IndexItem(
      itemId=self.itemId,
      indexId=self.indexId,
      fileId=self.fileId,
      blockId=self.blockId,
      spanId=self.spanId,
      value=self.value,
      externalId=self.externalId,
      externalType=self.externalType,
      metadata=self.metadata,
      embedding=self.embedding
    )
    if isinstance(ret.metadata, dict) or isinstance(ret.metadata, list):
      ret.metadata = json.dumps(ret.metadata)
    return ret

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "IndexItem":
    return IndexItem(
      itemId=d.get('itemId', None),
      indexId=d.get('indexId', None),
      fileId=d.get('fileId', None),
      blockId=d.get('blockId', None),
      spanId=d.get('spanId', None),
      value=d.get('value', None),
      externalId=d.get('externalId', None),
      externalType=d.get('externalType', None),
      metadata=d.get('metadata', None),
      embedding=d.get('embedding', None),
    )


@dataclass
class IndexInsertRequest(Request):
  indexId: str
  items: List[IndexItem] = None
  value: str = None
  fileId: str = None
  blockType: str = None
  externalId: str = None
  externalType: str = None
  metadata: any = None
  reindex: bool = True

@dataclass
class IndexItemId(Model):
  indexId: str = None
  id: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "IndexItemId":
    return IndexItemId(
      indexId = d.get('indexId', None),
      id = d.get('id', None)
    )

@dataclass
class IndexInsertResponse(Model):
  itemIds: List[IndexItemId] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "IndexInsertResponse":
    return IndexInsertResponse(
      itemIds = [IndexItemId.safely_from_dict(x) for x in (d.get('itemIds', []) or [])]
    )

@dataclass
class IndexEmbedRequest(Request):
  indexId: str

@dataclass
class IndexEmbedResponse(Model):
  indexId: str

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "IndexEmbedResponse":
    return IndexEmbedResponse(
      indexId = d.get('indexId', None)
    )

@dataclass
class IndexSearchRequest(Request):
  indexId: str
  query: str = None
  queries: List[str] = None
  k: int = 1  
  includeMetadata: bool = False

@dataclass
class IndexSearchResponse(Model):
  hits: List[Hit] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "IndexSearchResponse":
    hits = [Hit.safely_from_dict(h) for h in (d.get("hits", []) or [])]
    return IndexSearchResponse(
      hits=hits
    )

@dataclass
class IndexSnapshotRequest(Request):
  indexId: str
  # This variable is intended only to support
  # unit testing.
  windowSize: int = None

@dataclass
class IndexSnapshotResponse(Model):
  indexId: str
  snapshotId: str

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "IndexSnapshotResponse":
    return IndexSnapshotResponse(
      indexId = d.get('indexId', None),
      snapshotId = d.get('snapshotId', None)
    )

@dataclass
class ListSnapshotsRequest(Request):
  indexId: str = None

@dataclass
class ListSnapshotsResponse(Model):
  snapshots: List[IndexSnapshotResponse]
  
  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "IndexSnapshotResponse":
    return IndexSnapshotResponse(
      snapshots = [IndexSnapshotResponse.safely_from_dict(dd) for dd in (d.get('snapshots', []) or [])]
    )

@dataclass
class ListItemsRequest(Request):
  indexId: str = None
  fileId: str = None
  blockId: str = None
  spanId: str = None

@dataclass
class ListItemsResponse(Model):
  items: List[IndexItem]
  
  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ListItemsResponse":
    return ListItemsResponse(
      items = [IndexItem.safely_from_dict(dd) for dd in (d.get('items', []) or [])]
    )

@dataclass
class DeleteSnapshotsRequest(Request):
  snapshotId: str = None

@dataclass
class DeleteSnapshotsResponse(Request):
  snapshotId: str = None
