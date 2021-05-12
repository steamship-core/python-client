import logging
import json
from typing import Union, List, Dict

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
    resp = self.nludb.post('embedding-index/insert', req)
    return IndexInsertResponse.safely_from_dict(resp)

  def embed(self) -> IndexEmbedResponse:
    req = IndexEmbedRequest(
      self.id
    )
    resp = self.nludb.post('embedding-index/embed', req)
    IndexEmbedResponse.safely_from_dict(resp)

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
    resp = self.nludb.post('embedding-index/search', req)
    return IndexSearchResponse.safely_from_dict(resp)
