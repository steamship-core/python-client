import logging
import json
from typing import Union, List, Dict

from nludb import __version__
from nludb.api.base import ApiBase, AsyncTask, NludbResponse
from nludb.types.base import Metadata
from nludb.types.embedding_index import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class EmbeddingIndex:
  """A persistent, read-optimized index over embeddings.
  """

  def __init__(self, nludb: ApiBase, id: str, name: str):
    self.nludb = nludb
    self.name = name
    self.id = id

  def insert_file(
    self, 
    fileId: str,
    blockType: str = None,
    externalId: str = None,
    externalType: str = None,
    metadata: Union[int, float, bool, str, List, Dict] = None,
    reindex: bool = True
  ) -> NludbResponse[IndexInsertResponse]:    
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
    return self.nludb.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse
    )

  def insert_many(
    self,
    items: List[Union[IndexItem, str]],
    reindex: bool=True
  ) -> NludbResponse[IndexInsertResponse]:
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
    return self.nludb.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse
    )

  def insert(
    self, 
    value: str,
    externalId: str = None,
    externalType: str = None,
    metadata: Union[int, float, bool, str, List, Dict] = None,
    reindex: bool = True
  ) -> NludbResponse[IndexInsertResponse]:
    
    req = IndexInsertRequest(
      indexId=self.id,
      value=value,
      items=None,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata_to_str(metadata),
      reindex=reindex,
    )
    return self.nludb.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse
    )

  def embed(self) -> NludbResponse[IndexEmbedResponse]:
    req = IndexEmbedRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/embed',
      req,
      expect=IndexEmbedRequest,
      asynchronous=True
    )

  def create_snapshot(self) -> NludbResponse[IndexSnapshotResponse]:
    req = IndexSnapshotRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/snapshot/create',
      req,
      expect=IndexSnapshotRequest,
      asynchronous=True
    )

  def list_snapshots(self) -> NludbResponse[ListSnapshotsResponse]:
    req = ListSnapshotsRequest(
      indexId = self.id
    )
    return self.nludb.post(
      'embedding-index/snapshot/list',
      req,
      expect=ListSnapshotsResponse
    )

  def delete_snapshot(self, snapshot_id: str) -> NludbResponse[DeleteSnapshotsResponse]:
    req = DeleteSnapshotsRequest(
      snapshotId = snapshot_id
    )
    return self.nludb.post(
      'embedding-index/snapshot/delete',
      req,
      expect=DeleteSnapshotsResponse
    )

  def delete(self) -> NludbResponse[IndexDeleteResponse]:
    req = IndexDeleteRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/delete',
      req,
      expect=IndexDeleteResponse
    )

  def search(
    self, 
    query: Union[str, List[str]],
    k: int = 1,
    includeMetadata: bool = False
  ) -> NludbResponse[IndexSearchResponse]:
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
    return self.nludb.post(
      'embedding-index/search',
      req,
      expect=IndexSearchResponse
    )

  @staticmethod
  def create(
    nludb: ApiBase,
    name: str,
    model: str,
    upsert: bool = True,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None
  ) -> "EmbeddingIndex":
    req = IndexCreateRequest(
      name=name,
      model=model,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
    )
    res = nludb.post('embedding-index/create', req)
    return EmbeddingIndex(
      nludb=nludb,
      name=req.name,
      id=res.data.get("id", None)
    )