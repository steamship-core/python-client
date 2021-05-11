import logging
from nludb import __version__
from nludb.api.base import ApiBase
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
    metadata: any = None,
    reindex: bool = True
  ) -> IndexInsertResponse:
    req = IndexInsertRequest(
      indexId=self.id,
      value=value,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
      reindex=reindex,
    )
    resp = self.nludb.post('embedding-index/insert', req)
    return IndexInsertResponse(**resp)

  def embed(self) -> IndexEmbedResponse:
    req = IndexEmbedRequest(
      indexId=self.id
    )
    resp = self.nludb.post('embedding-index/embed', req)
    return IndexEmbedRequest(resp)

  def search(
    self, 
    query: str,
    k: int = 1,
    includeMetadata: bool = False
  ) -> IndexSearchResponse:
    req = IndexSearchRequest(
      indexId=self.id,
      query=query,
      k=k,
      includeMetadata=includeMetadata,
    )
    resp = self.nludb.post('embedding-index/search', req)
    return IndexSearchResponse(resp)
