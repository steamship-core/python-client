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
      self.id,
      value,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
      reindex=reindex,
    )
    return self.nludb.post(
      'embedding-index/insert',
      req,
      IndexInsertResponse
    )

  def embed(self) -> AsyncTask(IndexEmbedResponse):
    req = IndexEmbedRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/embed',
      req,
      IndexEmbedRequest,
      asynchronous=True
    )

  def delete(self) -> IndexDeleteResponse:
    req = IndexDeleteRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/delete',
      req,
      IndexDeleteResponse
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
      IndexSearchResponse
    )
