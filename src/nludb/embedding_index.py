import logging
import json
from dataclasses import dataclass
from typing import Union, List, Dict


from nludb import __version__
from nludb.base.base import ApiBase, Response
from nludb.base.requests import IdentifierRequest
from nludb.types.base import Metadata
from nludb.types.embedding_index import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

@dataclass
class EmbeddingIndex:
  """A persistent, read-optimized index over embeddings.
  """

  client: ApiBase = None
  id: str = None
  handle: str = None
  name: str = None
  model: str = None
  externalId: str = None
  externalType: str = None
  metadata: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "EmbeddingIndex":
    return EmbeddingIndex(
      client = client,
      id = d.get('id', None),
      handle = d.get('handle', None),
      name = d.get('name', None),
      model = d.get('model', None),
      externalId = d.get('externalId', None),
      externalType = d.get('externalType', None),
      metadata = d.get('metadata', None)
    )

  def insert_file(
    self, 
    fileId: str,
    blockType: str = None,
    externalId: str = None,
    externalType: str = None,
    metadata: Union[int, float, bool, str, List, Dict] = None,
    reindex: bool = True,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
  ) -> Response[IndexInsertResponse]:    
    if isinstance(metadata, dict) or isinstance(metadata, list):
      metadata = json.dumps(metadata)

    req = IndexInsertRequest(
      self.id,
      fileId=fileId,
      blockType=blockType,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
      reindex=reindex,
    )
    return self.client.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def insert_many(
    self,
    items: List[Union[IndexItem, str]],
    reindex: bool=True,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
  ) -> Response[IndexInsertResponse]:
    newItems = []
    for item in items:
      if type(item) == str:
        newItems.append(IndexItem(value=item))
      else:
        newItems.append(item)

    req = IndexInsertRequest(
      indexId=self.id,
      value=None,
      items=[item.clone_for_insert() for item in newItems],
      reindex=reindex,
    )
    return self.client.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def insert(
    self, 
    value: str,
    externalId: str = None,
    externalType: str = None,
    metadata: Union[int, float, bool, str, List, Dict] = None,
    reindex: bool = True,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
  ) -> Response[IndexInsertResponse]:
    
    req = IndexInsertRequest(
      indexId=self.id,
      value=value,
      items=None,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata_to_str(metadata),
      reindex=reindex,
    )
    return self.client.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def embed(
    self,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> Response[IndexEmbedResponse]:
    req = IndexEmbedRequest(
      self.id
    )
    return self.client.post(
      'embedding-index/embed',
      req,
      expect=IndexEmbedRequest,
      asynchronous=True,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def create_snapshot(
    self,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> Response[IndexSnapshotResponse]:
    req = IndexSnapshotRequest(
      self.id
    )
    return self.client.post(
      'embedding-index/snapshot/create',
      req,
      expect=IndexSnapshotRequest,
      asynchronous=True,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def list_snapshots(
    self,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> Response[ListSnapshotsResponse]:
    req = ListSnapshotsRequest(
      indexId = self.id
    )
    return self.client.post(
      'embedding-index/snapshot/list',
      req,
      expect=ListSnapshotsResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def list_items(
    self, 
    fileId: str = None, 
    blockId: str = None, 
    spanId: str = None,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> Response[ListItemsResponse]:
    req = ListItemsRequest(
      indexId = self.id,
      fileId = fileId,
      blockId = blockId,
      spanId = spanId
    )
    return self.client.post(
      'embedding-index/listItems',
      req,
      expect=ListItemsResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def delete_snapshot(
    self, 
    snapshot_id: str,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> Response[DeleteSnapshotsResponse]:
    req = DeleteSnapshotsRequest(
      snapshotId = snapshot_id
    )
    return self.client.post(
      'embedding-index/snapshot/delete',
      req,
      expect=DeleteSnapshotsResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def delete(
    self,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> "Response[EmbeddingIndex]":
    return self.client.post(
      'embedding-index/delete',
      IdentifierRequest(id=self.id),
      expect=EmbeddingIndex,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def search(
    self, 
    query: Union[str, List[str]],
    k: int = 1,
    includeMetadata: bool = False,
    pd = False,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
  ) -> Response[IndexSearchResponse]:
    if type(query) == list:
      req = IndexSearchRequest(
        self.id,
        query=None,
        queries=query,
        k=k,
        includeMetadata=includeMetadata,
      )
    else:
      req = IndexSearchRequest(
        self.id,
        query=query,
        queries=None,
        k=k,
        includeMetadata=includeMetadata,
      )
    ret = self.client.post(
      'embedding-index/search',
      req,
      expect=IndexSearchResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )
    
    if pd is False:
      return ret

    import pandas as pd # type: ignore 
    return pd.DataFrame([(hit.score, hit.value) for hit in ret.data.hits], columns =['Score', 'Value'])

  @staticmethod
  def create(
    client: ApiBase,
    handle: str = None,
    name: str = None,
    model: str = None,
    upsert: bool = True,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
  ) -> "Response[EmbeddingIndex]":
    req = IndexCreateRequest(
      handle=handle,
      name=name,
      model=model,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
    )
    return client.post(
      'embedding-index/create', 
      req,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space,
      expect=EmbeddingIndex
    )
