import logging
import json
from typing import Union, List, Dict

from nludb import __version__
from nludb.api.base import ApiBase, AsyncTask
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
  ) -> IndexInsertResponse:    
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
    items: List[IndexItem],
    reindex: bool=True
  ) -> IndexInsertResponse:
    req = IndexInsertRequest(
      indexId=self.id,
      value=None,
      items=[item.clone_for_insert() for item in items],
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
  ) -> IndexInsertResponse:
    
    if isinstance(metadata, dict) or isinstance(metadata, list):
      metadata = json.dumps(metadata)

    req = IndexInsertRequest(
      indexId=self.id,
      value=value,
      items=None,
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

  def embed(self) -> AsyncTask(IndexEmbedResponse):
    req = IndexEmbedRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/embed',
      req,
      expect=IndexEmbedRequest,
      asynchronous=True
    )

  def create_snapshot(self) -> AsyncTask(IndexSnapshotResponse):
    req = IndexSnapshotRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/snapshot/create',
      req,
      expect=IndexSnapshotRequest,
      asynchronous=True
    )

  def list_snapshots(self) -> AsyncTask(ListSnapshotsResponse):
    req = ListSnapshotsRequest(
      indexId = self.id
    )
    return self.nludb.post(
      'embedding-index/snapshot/list',
      req,
      expect=ListSnapshotsResponse
    )

  def delete_snapshot(self, snapshot_id: str) -> AsyncTask(DeleteSnapshotsResponse):
    req = DeleteSnapshotsRequest(
      snapshotId = snapshot_id
    )
    return self.nludb.post(
      'embedding-index/snapshot/delete',
      req,
      expect=DeleteSnapshotsResponse
    )

  def delete(self) -> IndexDeleteResponse:
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
    query: str,
    k: int = 1,
    includeMetadata: bool = False
  ) -> IndexSearchResponse:
    req = IndexSearchRequest(
      self.id,
      query,
      k=k,
      includeMetadata=includeMetadata,
    )
    return self.nludb.post(
      'embedding-index/search',
      req,
      expect=IndexSearchResponse,
      debug=True
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
      id=res.get("id", None)
    )